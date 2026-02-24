"""
CSV import and normalization engine.

Supports common bank CSV export formats:
  - Chase Checking / Credit Card
  - Bank of America Checking / Credit Card
  - Wells Fargo Checking
  - Generic (date, description, amount)

All parsing is local — no external calls.
"""
import hashlib
import io
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd

from app.schemas import TransactionCreate


# ──────────────────────────────────────────────
# Format detection heuristics
# ──────────────────────────────────────────────

# Each profile lists the expected column names (lower-cased) and a mapper
# that converts a raw row dict → normalised dict.

FORMAT_PROFILES = {
    "chase": {
        "required_cols": {"transaction date", "description", "amount"},
        "optional_cols": {"type", "category", "memo"},
    },
    "bofa": {
        "required_cols": {"date", "description", "amount"},
        "optional_cols": {"running bal."},
    },
    "wells_fargo": {
        "required_cols": {"date", "description", "deposits", "withdrawals"},
        "optional_cols": {"balance"},
    },
    "generic": {
        "required_cols": {"date", "description", "amount"},
        "optional_cols": set(),
    },
}


def _lower_cols(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def detect_format(df: pd.DataFrame) -> str:
    """Return the best-matching format profile name."""
    cols = set(df.columns)
    if "transaction date" in cols and "description" in cols:
        return "chase"
    if "deposits" in cols and "withdrawals" in cols:
        return "wells_fargo"
    if "date" in cols and "description" in cols and "amount" in cols:
        return "bofa"
    return "generic"


# ──────────────────────────────────────────────
# Per-format row normalisers
# ──────────────────────────────────────────────

def _parse_amount(value) -> float:
    """Parse an amount string like '$1,234.56' or '(500.00)' → float."""
    if value is None:
        return 0.0
    s = str(value).strip()
    # Parentheses → negative
    negative = s.startswith("(") and s.endswith(")")
    s = s.replace("(", "").replace(")", "").replace("$", "").replace(",", "").strip()
    try:
        amount = float(s)
    except ValueError:
        amount = 0.0
    return -abs(amount) if negative else amount


def _parse_date(value) -> Optional[datetime]:
    """Try multiple date formats."""
    if isinstance(value, datetime):
        return value
    if pd.isna(value):
        return None
    s = str(value).strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _fingerprint(date: datetime, description: str, amount: float, account: str) -> str:
    raw = f"{date.isoformat()}|{description.lower().strip()}|{amount:.2f}|{account}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _normalise_chase(row: dict, account_name: str) -> Optional[dict]:
    date = _parse_date(row.get("transaction date") or row.get("date"))
    if date is None:
        return None
    description = str(row.get("description", "")).strip()
    amount_raw = _parse_amount(row.get("amount", 0))
    # Chase: negative = debit, positive = credit
    amount = abs(amount_raw)
    tx_type = "credit" if amount_raw > 0 else "debit"
    return dict(date=date, description=description, amount=amount,
                transaction_type=tx_type, account_name=account_name)


def _normalise_bofa(row: dict, account_name: str) -> Optional[dict]:
    date = _parse_date(row.get("date"))
    if date is None:
        return None
    description = str(row.get("description", "")).strip()
    amount_raw = _parse_amount(row.get("amount", 0))
    amount = abs(amount_raw)
    tx_type = "credit" if amount_raw > 0 else "debit"
    return dict(date=date, description=description, amount=amount,
                transaction_type=tx_type, account_name=account_name)


def _normalise_wells_fargo(row: dict, account_name: str) -> Optional[dict]:
    date = _parse_date(row.get("date"))
    if date is None:
        return None
    description = str(row.get("description", "")).strip()
    deposits = abs(_parse_amount(row.get("deposits", 0) or 0))
    withdrawals = abs(_parse_amount(row.get("withdrawals", 0) or 0))
    if deposits > 0:
        amount = deposits
        tx_type = "credit"
    else:
        amount = withdrawals
        tx_type = "debit"
    return dict(date=date, description=description, amount=amount,
                transaction_type=tx_type, account_name=account_name)


def _normalise_generic(row: dict, account_name: str) -> Optional[dict]:
    # Accept 'date' or 'transaction date'
    date = _parse_date(row.get("date") or row.get("transaction date"))
    if date is None:
        return None
    description = str(row.get("description", row.get("memo", ""))).strip()
    amount_raw = _parse_amount(row.get("amount", row.get("debit", row.get("credit", 0))))
    amount = abs(amount_raw)
    tx_type = "credit" if amount_raw >= 0 else "debit"
    return dict(date=date, description=description, amount=amount,
                transaction_type=tx_type, account_name=account_name)


NORMALISERS = {
    "chase": _normalise_chase,
    "bofa": _normalise_bofa,
    "wells_fargo": _normalise_wells_fargo,
    "generic": _normalise_generic,
}


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def parse_csv(
    file_bytes: bytes,
    account_name: str = "Imported Account",
    encoding: str = "utf-8-sig",
) -> Tuple[List[TransactionCreate], List[str]]:
    """
    Parse raw CSV bytes into a list of TransactionCreate objects.
    Returns (transactions, error_messages).
    """
    errors: List[str] = []
    transactions: List[TransactionCreate] = []

    # Try to read the CSV, handle encoding issues gracefully
    try:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding=encoding, dtype=str)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1", dtype=str)
        except Exception as exc:
            return [], [f"Failed to read CSV: {exc}"]
    except Exception as exc:
        return [], [f"Failed to read CSV: {exc}"]

    df = _lower_cols(df)

    # Drop completely empty rows
    df = df.dropna(how="all")

    if df.empty:
        return [], ["CSV file appears to be empty."]

    fmt = detect_format(df)
    normalise = NORMALISERS[fmt]

    for idx, row in df.iterrows():
        row_num = int(idx) + 2  # type: ignore[arg-type]
        row_dict = row.to_dict()
        try:
            normalised = normalise(row_dict, account_name)
        except Exception as exc:
            errors.append(f"Row {row_num}: parse error — {exc}")
            continue

        if normalised is None:
            errors.append(f"Row {row_num}: could not parse date, skipped.")
            continue

        if normalised["amount"] == 0:
            # Skip zero-dollar rows (common in statement CSVs)
            continue

        fp = _fingerprint(
            normalised["date"],
            normalised["description"],
            normalised["amount"],
            normalised["account_name"],
        )

        transactions.append(
            TransactionCreate(
                date=normalised["date"],
                description=normalised["description"],
                amount=normalised["amount"],
                transaction_type=normalised["transaction_type"],
                account_name=normalised["account_name"],
                fingerprint=fp,
                categorization_method="unset",
            )
        )

    return transactions, errors
