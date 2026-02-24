"""
CRUD operations for all database models.
All reads and writes go through these functions — no raw SQL in routes.
"""
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func, desc, asc
from sqlalchemy.orm import Session

from app import models, schemas


# ──────────────────────────────────────────────
# Category CRUD
# ──────────────────────────────────────────────

def get_categories(db: Session) -> List[models.Category]:
    return db.query(models.Category).order_by(asc(models.Category.name)).all()


def get_category_by_id(db: Session, category_id: int) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Optional[models.Category]:
    return (
        db.query(models.Category)
        .filter(func.lower(models.Category.name) == func.lower(name))
        .first()
    )


def create_category(db: Session, payload: schemas.CategoryCreate) -> models.Category:
    obj = models.Category(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_category(
    db: Session, category_id: int, payload: schemas.CategoryUpdate
) -> Optional[models.Category]:
    obj = get_category_by_id(db, category_id)
    if not obj:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_category(db: Session, category_id: int) -> bool:
    obj = get_category_by_id(db, category_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ──────────────────────────────────────────────
# Transaction CRUD
# ──────────────────────────────────────────────

def get_transactions(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
) -> Tuple[int, List[models.Transaction]]:
    query = db.query(models.Transaction)

    if category:
        query = query.filter(models.Transaction.category == category)
    if transaction_type:
        query = query.filter(models.Transaction.transaction_type == transaction_type)
    if start_date:
        query = query.filter(models.Transaction.date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.date <= end_date)
    if search:
        query = query.filter(
            models.Transaction.description.ilike(f"%{search}%")
        )

    total = query.count()
    items = (
        query.order_by(desc(models.Transaction.date))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, items


def get_transaction_by_id(db: Session, transaction_id: int) -> Optional[models.Transaction]:
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id)
        .first()
    )


def get_transaction_by_fingerprint(
    db: Session, fingerprint: str
) -> Optional[models.Transaction]:
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.fingerprint == fingerprint)
        .first()
    )


def create_transaction(
    db: Session, payload: schemas.TransactionCreate
) -> models.Transaction:
    data = payload.model_dump()
    # Link category_id from category name
    if data.get("category"):
        cat = get_category_by_name(db, data["category"])
        data["category_id"] = cat.id if cat else None
    obj = models.Transaction(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def bulk_create_transactions(
    db: Session, payloads: List[schemas.TransactionCreate]
) -> Tuple[int, int]:
    """Insert new transactions, skip duplicates. Returns (inserted, skipped)."""
    inserted = 0
    skipped = 0
    for payload in payloads:
        if get_transaction_by_fingerprint(db, payload.fingerprint):
            skipped += 1
            continue
        data = payload.model_dump()
        if data.get("category"):
            cat = get_category_by_name(db, data["category"])
            data["category_id"] = cat.id if cat else None
        obj = models.Transaction(**data)
        db.add(obj)
        inserted += 1
    db.commit()
    return inserted, skipped


def update_transaction(
    db: Session, transaction_id: int, payload: schemas.TransactionUpdate
) -> Optional[models.Transaction]:
    obj = get_transaction_by_id(db, transaction_id)
    if not obj:
        return None
    updates = payload.model_dump(exclude_unset=True)
    # If category name was updated, sync category_id
    if "category" in updates and updates["category"]:
        cat = get_category_by_name(db, updates["category"])
        updates["category_id"] = cat.id if cat else None
        updates["categorization_method"] = "manual"
    for field, value in updates.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_transaction(db: Session, transaction_id: int) -> bool:
    obj = get_transaction_by_id(db, transaction_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def get_uncategorized_transactions(db: Session) -> List[models.Transaction]:
    return (
        db.query(models.Transaction)
        .filter(
            (models.Transaction.category == None)
            | (models.Transaction.category == "Other")
        )
        .all()
    )


def get_categorized_transactions(db: Session) -> List[models.Transaction]:
    """Return transactions that have a real (non-null, non-Other) category for ML training."""
    return (
        db.query(models.Transaction)
        .filter(
            models.Transaction.category != None,
            models.Transaction.category != "Other",
            models.Transaction.category != "",
        )
        .all()
    )


def mark_subscriptions(db: Session, descriptions: List[str]) -> None:
    """Flag transactions whose description is in the subscription list."""
    db.query(models.Transaction).filter(
        models.Transaction.description.in_(descriptions)
    ).update({"is_subscription": True}, synchronize_session="fetch")
    db.commit()


# ──────────────────────────────────────────────
# Rule CRUD
# ──────────────────────────────────────────────

def get_rules(db: Session) -> List[models.Rule]:
    return (
        db.query(models.Rule)
        .order_by(desc(models.Rule.priority), asc(models.Rule.keyword))
        .all()
    )


def get_rule_by_id(db: Session, rule_id: int) -> Optional[models.Rule]:
    return db.query(models.Rule).filter(models.Rule.id == rule_id).first()


def create_rule(db: Session, payload: schemas.RuleCreate) -> models.Rule:
    data = payload.model_dump()
    cat = get_category_by_name(db, data["category"])
    data["category_id"] = cat.id if cat else None
    obj = models.Rule(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_rule(
    db: Session, rule_id: int, payload: schemas.RuleUpdate
) -> Optional[models.Rule]:
    obj = get_rule_by_id(db, rule_id)
    if not obj:
        return None
    updates = payload.model_dump(exclude_unset=True)
    if "category" in updates and updates["category"]:
        cat = get_category_by_name(db, updates["category"])
        updates["category_id"] = cat.id if cat else None
    for field, value in updates.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_rule(db: Session, rule_id: int) -> bool:
    obj = get_rule_by_id(db, rule_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ──────────────────────────────────────────────
# Monthly Summary CRUD
# ──────────────────────────────────────────────

def upsert_monthly_summary(
    db: Session, year: int, month: int
) -> models.MonthlySummary:
    """Recompute and save the monthly summary for the given year/month."""
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)

    rows = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.date >= start,
            models.Transaction.date < end,
        )
        .all()
    )

    income = sum(t.amount for t in rows if t.transaction_type == "credit")
    expenses = abs(sum(t.amount for t in rows if t.transaction_type == "debit"))
    net = income - expenses
    savings_rate = (net / income * 100) if income > 0 else 0.0

    # Add jobs income for current month
    now = datetime.utcnow()
    if year == now.year and month == now.month:
        jobs = db.query(models.Job).all()
        jobs_total = 0.0
        for j in jobs:
            base = (j.hourly_wage or 0.0) * (j.expected_shifts or 0) * (j.hours_per_shift or 0.0)
            ot = (j.hourly_wage or 0.0) * (j.ot1_5_hours or 0.0) * 1.5 + (j.hourly_wage or 0.0) * (j.ot2_hours or 0.0) * 2
            jobs_total += base + ot
        income += jobs_total
        net = income - expenses
        savings_rate = (net / income * 100) if income > 0 else 0.0

    obj = (
        db.query(models.MonthlySummary)
        .filter(
            models.MonthlySummary.year == year,
            models.MonthlySummary.month == month,
        )
        .first()
    )
    if obj is None:
        obj = models.MonthlySummary(year=year, month=month)
        db.add(obj)

    obj.total_income = round(income, 2)
    obj.total_expenses = round(expenses, 2)
    obj.net = round(net, 2)
    obj.savings_rate = round(savings_rate, 2)
    obj.transaction_count = len(rows)
    obj.computed_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return obj


def get_monthly_summaries(
    db: Session, limit: int = 12
) -> List[models.MonthlySummary]:
    return (
        db.query(models.MonthlySummary)
        .order_by(
            desc(models.MonthlySummary.year),
            desc(models.MonthlySummary.month),
        )
        .limit(limit)
        .all()
    )


# ──────────────────────────────────────────────
# Spending Alert CRUD
# ──────────────────────────────────────────────

def get_alerts(db: Session) -> List[models.SpendingAlert]:
    return db.query(models.SpendingAlert).order_by(asc(models.SpendingAlert.category)).all()


def get_alert_by_category(db: Session, category: str) -> Optional[models.SpendingAlert]:
    return (
        db.query(models.SpendingAlert)
        .filter(func.lower(models.SpendingAlert.category) == func.lower(category))
        .first()
    )


def upsert_alert(
    db: Session, payload: schemas.SpendingAlertCreate
) -> models.SpendingAlert:
    obj = get_alert_by_category(db, payload.category)
    if obj:
        obj.monthly_limit = payload.monthly_limit
        obj.is_active = payload.is_active
    else:
        obj = models.SpendingAlert(**payload.model_dump())
        db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def delete_alert(db: Session, alert_id: int) -> bool:
    obj = db.query(models.SpendingAlert).filter(models.SpendingAlert.id == alert_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# 
# ──────────────────────────────────────────────
# Jobs CRUD
# ──────────────────────────────────────────────


def get_jobs(db: Session) -> List[models.Job]:
    return db.query(models.Job).order_by(asc(models.Job.created_at)).all()


def get_job_by_id(db: Session, job_id: int) -> Optional[models.Job]:
    return db.query(models.Job).filter(models.Job.id == job_id).first()


def create_job(db: Session, payload: schemas.JobCreate) -> models.Job:
    obj = models.Job(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_job(db: Session, job_id: int, payload: schemas.JobUpdate) -> Optional[models.Job]:
    obj = get_job_by_id(db, job_id)
    if not obj:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_job(db: Session, job_id: int) -> bool:
    obj = get_job_by_id(db, job_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
