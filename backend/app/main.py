"""
FastAPI backend for the personal finance tracker.
All data stays local — no external APIs, no cloud storage.
"""
import hashlib
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import analytics, crud, models, rule_engine
from app.analytics import detect_subscriptions, CATEGORY_COLOURS
from app.config import ALLOWED_ORIGINS, DEFAULT_CATEGORIES, DEFAULT_RULES
from app.csv_importer import parse_csv
from app.database import SessionLocal, engine
from app.ml_classifier import predict, retrain_from_db
from app.schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    DashboardSummary,
    ImportResponse,
    MonthlySummaryOut,
    ProjectionResponse,
    RetrainResponse,
    RuleCreate,
    RuleOut,
    RuleUpdate,
    SpendingAlertCreate,
    SpendingAlertOut,
    SpendingAlertUpdate,
    SubscriptionItem,
    TransactionCreate,
    TransactionListResponse,
    TransactionOut,
    TransactionUpdate,
    JobCreate,
    JobOut,
    JobUpdate,
)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Personal Finance Tracker",
    description="Local-only finance tracking with privacy-first design",
    version="1.0.0",
)

# CORS middleware — restrict origins to localhost (dev) and deployed frontend (production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ──────────────────────────────────────────────
# Health check endpoint
# ──────────────────────────────────────────────

@app.get("/")
def health_check():
    """Health check endpoint for Render and deployment platforms."""
    return {"status": "ok"}


# ──────────────────────────────────────────────
# Startup tasks
# ──────────────────────────────────────────────

@app.on_event("startup")
def startup_event():
    """Seed default categories and rules on first run."""
    db = SessionLocal()
    try:
        # Seed categories
        if not crud.get_categories(db):
            for i, cat_name in enumerate(DEFAULT_CATEGORIES):
                color = CATEGORY_COLOURS[i % len(CATEGORY_COLOURS)]
                crud.create_category(db, CategoryCreate(name=cat_name, color=color))
            # Set budget limits for some categories
            groceries = crud.get_category_by_name(db, "Groceries")
            if groceries:
                crud.update_category(db, groceries.id, CategoryUpdate(budget_limit=500.0))
            gas = crud.get_category_by_name(db, "Gas & Fuel")
            if gas:
                crud.update_category(db, gas.id, CategoryUpdate(budget_limit=200.0))
            dining = crud.get_category_by_name(db, "Dining Out")
            if dining:
                crud.update_category(db, dining.id, CategoryUpdate(budget_limit=300.0))
            entertainment = crud.get_category_by_name(db, "Entertainment")
            if entertainment:
                crud.update_category(db, entertainment.id, CategoryUpdate(budget_limit=150.0))
        else:
            # Update colors for existing categories
            categories = crud.get_categories(db)
            for i, cat in enumerate(categories):
                color = CATEGORY_COLOURS[i % len(CATEGORY_COLOURS)]
                crud.update_category(db, cat.id, CategoryUpdate(color=color))
            # Set budget limits if not set
            for cat in categories:
                if cat.budget_limit is None:
                    if cat.name == "Groceries":
                        crud.update_category(db, cat.id, CategoryUpdate(budget_limit=500.0))
                    elif cat.name == "Gas & Fuel":
                        crud.update_category(db, cat.id, CategoryUpdate(budget_limit=200.0))
                    elif cat.name == "Dining Out":
                        crud.update_category(db, cat.id, CategoryUpdate(budget_limit=300.0))
                    elif cat.name == "Entertainment":
                        crud.update_category(db, cat.id, CategoryUpdate(budget_limit=150.0))

            # Create alerts for categories with budget limits
            for cat in categories:
                if cat.budget_limit is not None and cat.budget_limit > 0:
                    crud.upsert_alert(db, SpendingAlertCreate(category=cat.name, monthly_limit=cat.budget_limit, is_active=True))

        # Seed rules
        if not crud.get_rules(db):
            for keyword, category, priority in DEFAULT_RULES:
                crud.create_rule(db, RuleCreate(keyword=keyword, category=category, priority=priority))

        # Create alerts for categories with budget limits
        categories = crud.get_categories(db)
        for cat in categories:
            if cat.budget_limit is not None and cat.budget_limit > 0:
                crud.upsert_alert(db, SpendingAlertCreate(category=cat.name, monthly_limit=cat.budget_limit, is_active=True))

        # Seed sample transactions if database is empty
        existing_txns = db.query(models.Transaction).first()
        if not existing_txns:
            from app.models import Transaction
            sample_transactions = [
                Transaction(date=datetime(2026, 2, 1), description="Salary Deposit", amount=3500.00, transaction_type="credit", account_name="Checking", category="Income", categorization_method="rule", fingerprint=hashlib.sha256(b"2026-02-01|salary deposit|3500.00|checking").hexdigest(), notes="Monthly salary"),
                Transaction(date=datetime(2026, 2, 2), description="Whole Foods Market", amount=125.50, transaction_type="debit", account_name="Checking", category="Groceries", categorization_method="rule", fingerprint=hashlib.sha256(b"2026-02-02|whole foods market|125.50|checking").hexdigest()),
                Transaction(date=datetime(2026, 2, 3), description="Starbucks Coffee", amount=5.75, transaction_type="debit", account_name="Checking", category="Dining Out", categorization_method="rule", fingerprint=hashlib.sha256(b"2026-02-03|starbucks coffee|5.75|checking").hexdigest()),
                Transaction(date=datetime(2026, 2, 4), description="Netflix Subscription", amount=15.99, transaction_type="debit", account_name="Checking", category="Subscriptions", categorization_method="rule", fingerprint=hashlib.sha256(b"2026-02-04|netflix subscription|15.99|checking").hexdigest()),
                Transaction(date=datetime(2026, 2, 5), description="Shell Gas Station", amount=45.00, transaction_type="debit", account_name="Checking", category="Gas & Fuel", categorization_method="rule", fingerprint=hashlib.sha256(b"2026-02-05|shell gas station|45.00|checking").hexdigest()),
                Transaction(date=datetime(2026, 2, 6), description="Rent Payment", amount=1500.00, transaction_type="debit", account_name="Checking", category="Rent & Housing", categorization_method="rule", fingerprint=hashlib.sha256(b"2026-02-06|rent payment|1500.00|checking").hexdigest()),
                Transaction(date=datetime(2026, 2, 8), description="Trader Joe's", amount=85.30, transaction_type="debit", account_name="Checking", category="Groceries", categorization_method="rule", fingerprint=hashlib.sha256(b"2026-02-08|trader joe's|85.30|checking").hexdigest()),
                Transaction(date=datetime(2026, 2, 10), description="Chipotle", amount=12.45, transaction_type="debit", account_name="Checking", category="Dining Out", categorization_method="rule", fingerprint=hashlib.sha256(b"2026-02-10|chipotle|12.45|checking").hexdigest()),
                Transaction(date=datetime(2026, 2, 12), description="Spotify Premium", amount=11.99, transaction_type="debit", account_name="Checking", category="Subscriptions", categorization_method="rule", fingerprint=hashlib.sha256(b"2026-02-12|spotify premium|11.99|checking").hexdigest()),
                Transaction(date=datetime(2026, 2, 14), description="Electric Bill", amount=120.00, transaction_type="debit", account_name="Checking", category="Utilities", categorization_method="rule", fingerprint=hashlib.sha256(b"2026-02-14|electric bill|120.00|checking").hexdigest()),
                Transaction(date=datetime(2026, 2, 15), description="Doctor Visit", amount=200.00, transaction_type="debit", account_name="Checking", category="Healthcare", categorization_method="rule", fingerprint=hashlib.sha256(b"2026-02-15|doctor visit|200.00|checking").hexdigest()),
                Transaction(date=datetime(2026, 2, 16), description="Target Shopping", amount=65.20, transaction_type="debit", account_name="Checking", category="Shopping", categorization_method="rule", fingerprint=hashlib.sha256(b"2026-02-16|target shopping|65.20|checking").hexdigest()),
                Transaction(date=datetime(2026, 2, 18), description="Movie Tickets", amount=28.00, transaction_type="debit", account_name="Checking", category="Entertainment", categorization_method="rule", fingerprint=hashlib.sha256(b"2026-02-18|movie tickets|28.00|checking").hexdigest()),
            ]
            for txn in sample_transactions:
                db.add(txn)
            db.commit()
            logger.info("Sample transactions seeded.")

        # Create monthly summary for current month
        now = datetime.utcnow()
        crud.upsert_monthly_summary(db, now.year, now.month)

        logger.info("Database initialization complete.")
    finally:
        db.close()


# ──────────────────────────────────────────────
# Category endpoints
# ──────────────────────────────────────────────

@app.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """List all categories."""
    return crud.get_categories(db)


@app.post("/categories", response_model=CategoryOut)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    return crud.create_category(db, payload)


@app.put("/categories/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)
):
    """Update an existing category."""
    obj = crud.update_category(db, category_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    return obj


@app.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category."""
    if not crud.delete_category(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}


# ──────────────────────────────────────────────
# Transaction endpoints
# ──────────────────────────────────────────────

@app.get("/transactions", response_model=TransactionListResponse)
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List transactions with optional filtering."""
    total, items = crud.get_transactions(
        db, page, page_size, category, transaction_type, start_date, end_date, search
    )
    return TransactionListResponse(
        total=total, page=page, page_size=page_size, items=items
    )


@app.post("/transactions", response_model=TransactionOut)
def create_transaction_manually(payload: TransactionCreate, db: Session = Depends(get_db)):
    """Create a single transaction manually."""
    # Generate fingerprint if not provided
    if not payload.fingerprint:
        raw = f"{payload.date.isoformat()}|{payload.description.lower().strip()}|{payload.amount:.2f}|{payload.account_name or ''}"
        payload.fingerprint = hashlib.sha256(raw.encode()).hexdigest()
    
    # Apply rules for categorization
    rules = crud.get_rules(db)
    category = rule_engine.apply_rules(payload.description, rules)
    if category:
        payload.category = category
        payload.categorization_method = "rule"
    else:
        # Try ML fallback
        ml_category = predict(payload.description)
        if ml_category:
            payload.category = ml_category
            payload.categorization_method = "ml"

    obj = crud.create_transaction(db, payload)

    # Update monthly summaries
    now = datetime.utcnow()
    crud.upsert_monthly_summary(db, now.year, now.month)

    return obj


@app.put("/transactions/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db)
):
    """Update a transaction (e.g., manual category override)."""
    obj = crud.update_transaction(db, transaction_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return obj


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Delete a transaction."""
    if not crud.delete_transaction(db, transaction_id):
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted"}


# ──────────────────────────────────────────────
# CSV Import
# ──────────────────────────────────────────────

@app.post("/import", response_model=ImportResponse)
def import_csv(
    file: UploadFile = File(...),
    account_name: str = "Imported Account",
    db: Session = Depends(get_db),
):
    """Import transactions from a CSV file."""
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        contents = file.file.read()
        transactions, errors = parse_csv(contents, account_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {e}")

    # Categorize with rules
    rules = crud.get_rules(db)
    for tx in transactions:
        category = rule_engine.apply_rules(tx.description, rules)
        if category:
            tx.category = category
            tx.categorization_method = "rule"
        else:
            # Try ML fallback
            ml_category = predict(tx.description)
            if ml_category:
                tx.category = ml_category
                tx.categorization_method = "ml"

    # Bulk insert
    inserted, skipped = crud.bulk_create_transactions(db, transactions)

    # Update monthly summaries
    now = datetime.utcnow()
    crud.upsert_monthly_summary(db, now.year, now.month)

    return ImportResponse(
        imported=inserted,
        duplicates=skipped,
        errors=len(errors),
        messages=errors,
    )


# ──────────────────────────────────────────────
# Rule endpoints
# ──────────────────────────────────────────────

@app.get("/rules", response_model=List[RuleOut])
def list_rules(db: Session = Depends(get_db)):
    """List all categorization rules."""
    return crud.get_rules(db)


@app.post("/rules", response_model=RuleOut)
def create_rule(payload: RuleCreate, db: Session = Depends(get_db)):
    """Create a new categorization rule."""
    return crud.create_rule(db, payload)


@app.put("/rules/{rule_id}", response_model=RuleOut)
def update_rule(rule_id: int, payload: RuleUpdate, db: Session = Depends(get_db)):
    """Update an existing rule."""
    obj = crud.update_rule(db, rule_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Rule not found")
    return obj


@app.delete("/rules/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a rule."""
    if not crud.delete_rule(db, rule_id):
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule deleted"}


# ──────────────────────────────────────────────
# Spending Alerts
# ──────────────────────────────────────────────

@app.get("/alerts", response_model=List[SpendingAlertOut])
def list_alerts(db: Session = Depends(get_db)):
    """List all spending alerts."""
    return crud.get_alerts(db)


@app.post("/alerts", response_model=SpendingAlertOut)
def create_alert(payload: SpendingAlertCreate, db: Session = Depends(get_db)):
    """Create or update a spending alert."""
    return crud.upsert_alert(db, payload)


@app.put("/alerts/{alert_id}", response_model=SpendingAlertOut)
def update_alert(
    alert_id: int, payload: SpendingAlertUpdate, db: Session = Depends(get_db)
):
    """Update an alert."""
    obj = db.query(models.SpendingAlert).filter(models.SpendingAlert.id == alert_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Alert not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@app.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert."""
    if not crud.delete_alert(db, alert_id):
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert deleted"}


# ──────────────────────────────────────────────
# Jobs (Income entries)
# ──────────────────────────────────────────────

@app.get("/jobs", response_model=List[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    """List all job entries."""
    return crud.get_jobs(db)


@app.post("/jobs", response_model=JobOut)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    """Create a new job entry."""
    obj = crud.create_job(db, payload)
    # Update monthly summary for current month
    now = datetime.utcnow()
    crud.upsert_monthly_summary(db, now.year, now.month)
    return obj


@app.put("/jobs/{job_id}", response_model=JobOut)
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db)):
    """Update an existing job entry."""
    obj = crud.update_job(db, job_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Job not found")
    # Update monthly summary for current month
    now = datetime.utcnow()
    crud.upsert_monthly_summary(db, now.year, now.month)
    return obj


@app.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job entry."""
    if not crud.delete_job(db, job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    # Update monthly summary for current month
    now = datetime.utcnow()
    crud.upsert_monthly_summary(db, now.year, now.month)
    return {"message": "Job deleted"}


# ──────────────────────────────────────────────
# Analytics & Dashboard
# ──────────────────────────────────────────────

@app.get("/dashboard", response_model=DashboardSummary)
def get_dashboard(db: Session = Depends(get_db)):
    """Get dashboard summary with current month metrics."""
    return analytics.build_dashboard(db)


@app.get("/subscriptions", response_model=List[SubscriptionItem])
def get_subscriptions(db: Session = Depends(get_db)):
    """Detect and list potential subscription charges."""
    return detect_subscriptions(db)


@app.get("/projection", response_model=ProjectionResponse)
def get_projection(
    initial_balance: float = Query(..., gt=0),
    monthly_contribution: float = Query(..., ge=0),
    annual_return_pct: float = Query(5.0, ge=0, le=50),
    months: int = Query(60, ge=1, le=1200),
):
    """Calculate 5-year financial projection."""
    return analytics.compute_projection(
        initial_balance, monthly_contribution, annual_return_pct, months
    )


@app.get("/monthly-summaries", response_model=List[MonthlySummaryOut])
def get_monthly_summaries(limit: int = Query(12, ge=1, le=120), db: Session = Depends(get_db)):
    """Get historical monthly summaries."""
    return crud.get_monthly_summaries(db, limit)


# ──────────────────────────────────────────────
# ML Model Management
# ──────────────────────────────────────────────

@app.post("/retrain", response_model=RetrainResponse)
def retrain_model(db: Session = Depends(get_db)):
    """Retrain the ML classifier on current categorized transactions."""
    success, samples, accuracy = retrain_from_db(db)
    if success:
        message = f"Model retrained on {samples} samples"
        if accuracy:
            message += f" with {accuracy:.1%} cross-validation accuracy"
    else:
        message = f"Training failed. Only {samples} samples available (need at least 30)."
    return RetrainResponse(
        status="success" if success else "failed",
        training_samples=samples,
        accuracy=accuracy,
        message=message,
    )


# ──────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}