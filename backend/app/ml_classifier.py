"""
ML-based fallback classifier.

Architecture:
  - TF-IDF vectorizer on transaction descriptions
  - Logistic Regression classifier
  - Trained on already-categorised transactions in the local DB
  - Model persisted to disk with joblib (no cloud, no telemetry)

The classifier is used ONLY when no rule matches a description.
It automatically retrains when ≥ MIN_TRAINING_SAMPLES labelled rows exist
and the model file is older than the newest manually-categorised transaction.
"""
import logging
from pathlib import Path
from typing import List, Optional, Tuple

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

from app.config import CLASSIFIER_PATH, MIN_TRAINING_SAMPLES, TFIDF_VECTORIZER_PATH

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Internal state (loaded lazily)
# ──────────────────────────────────────────────
_pipeline: Optional[Pipeline] = None
_classes: Optional[List[str]] = None


def _build_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=(1, 2),
                    min_df=1,
                    max_features=5000,
                    sublinear_tf=True,
                    strip_accents="unicode",
                    lowercase=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    solver="lbfgs",
                    multi_class="auto",
                    C=5.0,
                ),
            ),
        ]
    )


def _model_exists() -> bool:
    return Path(CLASSIFIER_PATH).exists() and Path(TFIDF_VECTORIZER_PATH).exists()


def load_model() -> bool:
    """
    Load the persisted pipeline from disk into module-level state.
    Returns True on success, False if no model file exists.
    """
    global _pipeline, _classes
    if not _model_exists():
        return False
    try:
        _pipeline = joblib.load(CLASSIFIER_PATH)
        _classes = joblib.load(TFIDF_VECTORIZER_PATH)
        logger.info("ML model loaded from disk.")
        return True
    except Exception as exc:
        logger.warning("Failed to load ML model: %s", exc)
        _pipeline = None
        _classes = None
        return False


def train(
    descriptions: List[str],
    labels: List[str],
) -> Tuple[bool, int, Optional[float]]:
    """
    Train (or retrain) the classifier.

    Args:
        descriptions: list of transaction description strings
        labels: matching category names

    Returns:
        (success, sample_count, cv_accuracy)
    """
    global _pipeline, _classes

    if len(descriptions) < MIN_TRAINING_SAMPLES:
        logger.info(
            "Not enough training samples (%d < %d). Skipping training.",
            len(descriptions),
            MIN_TRAINING_SAMPLES,
        )
        return False, len(descriptions), None

    unique_labels = list(set(labels))
    if len(unique_labels) < 2:
        logger.warning("Need at least 2 distinct categories to train. Got %d.", len(unique_labels))
        return False, len(descriptions), None

    pipeline = _build_pipeline()

    # Cross-validate to estimate accuracy before persisting
    cv_folds = min(5, len(descriptions) // max(len(unique_labels), 1))
    cv_folds = max(cv_folds, 2)
    try:
        scores = cross_val_score(pipeline, descriptions, labels, cv=cv_folds, scoring="accuracy")
        accuracy = float(np.mean(scores))
    except Exception:
        accuracy = None

    # Fit on full dataset
    pipeline.fit(descriptions, labels)

    # Persist
    joblib.dump(pipeline, CLASSIFIER_PATH)
    joblib.dump(unique_labels, TFIDF_VECTORIZER_PATH)

    _pipeline = pipeline
    _classes = unique_labels

    logger.info(
        "ML model trained on %d samples. CV accuracy: %s",
        len(descriptions),
        f"{accuracy:.3f}" if accuracy is not None else "N/A",
    )
    return True, len(descriptions), accuracy


def predict(description: str) -> Optional[str]:
    """
    Predict the category for a single transaction description.
    Returns None if the model is not loaded or confidence is too low.
    """
    global _pipeline
    if _pipeline is None:
        if not load_model():
            return None

    try:
        pred = _pipeline.predict([description])
        return str(pred[0])
    except Exception as exc:
        logger.warning("ML prediction failed: %s", exc)
        return None


def predict_with_confidence(description: str) -> Tuple[Optional[str], float]:
    """
    Returns (category, confidence) where confidence ∈ [0, 1].
    Returns (None, 0.0) if the model is unavailable.
    """
    global _pipeline
    if _pipeline is None:
        if not load_model():
            return None, 0.0

    try:
        proba = _pipeline.predict_proba([description])[0]
        max_idx = int(np.argmax(proba))
        confidence = float(proba[max_idx])
        classes = _pipeline.classes_
        category = str(classes[max_idx])
        return category, confidence
    except Exception as exc:
        logger.warning("ML confidence prediction failed: %s", exc)
        return None, 0.0


def retrain_from_db(db) -> Tuple[bool, int, Optional[float]]:
    """
    Pull all categorised transactions from the DB and retrain.
    Designed to be called from an API endpoint or background task.
    """
    from app.crud import get_categorized_transactions

    transactions = get_categorized_transactions(db)
    if not transactions:
        return False, 0, None

    descriptions = [t.description for t in transactions]
    labels = [t.category for t in transactions]

    return train(descriptions, labels)


def is_model_ready() -> bool:
    """Check whether a trained model is available."""
    return _pipeline is not None or _model_exists()
