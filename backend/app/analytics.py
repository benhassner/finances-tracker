"""
Analytics engine — computes dashboard metrics, projections, and subscription detection.
All computation happens locally; no data leaves the machine.
"""
import calendar
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, crud
from app.config import SUBSCRIPTION_AMOUNT_TOLERANCE, SUBSCRIPTION_MIN_OCCURRENCES
from app.schemas import (
    CategorySpend,
    DashboardSummary,
    MonthlyTrend,
    ProjectionDataPoint,
    ProjectionResponse,
    SubscriptionItem,
)

logger = logging.getLogger(__name__)

# Colour palette for categories (cycles if more than palette length)
CATEGORY_COLOURS = [
    "#6366f1", "#ec4899", "#f59e0b", "#10b981", "#3b82f6",
    "#ef4444", "#8b5cf6", "#14b8a6", "#f97316", "#84cc16",
    "#06b6d4", "#a855f7", "#eab308", "#22c55e", "#64748b",
    "#e11d48",
]


def _month_label(year: int, month: int) -> str:
    return f"{calendar.month_abbr[month]} {year}"


# ──────────────────────────────────────────────
# Category breakdown
# ──────────────────────────────────────────────

def spending_by_category(
    db: Session,
    year: int,
    month: int,
    *,
    category_colours: Optional[Dict[str, str]] = None,
) -> List[CategorySpend]:
    """Return debit totals grouped by category for a given month."""
    start = datetime(year, month, 1)
    end_month = month + 1 if month < 12 else 1
    end_year = year if month < 12 else year + 1
    end = datetime(end_year, end_month, 1)

    rows = (
        db.query(
            models.Transaction.category,
            func.sum(models.Transaction.amount).label("total"),
            func.count(models.Transaction.id).label("cnt"),
        )
        .filter(
            models.Transaction.date >= start,
            models.Transaction.date < end,
            models.Transaction.transaction_type == "debit",
        )
        .group_by(models.Transaction.category)
        .order_by(func.sum(models.Transaction.amount).desc())
        .all()
    )

    # Fetch category colours from DB
    if category_colours is None:
        cats = db.query(models.Category).all()
        category_colours = {c.name: c.color for c in cats}

    result = []
    for i, row in enumerate(rows):
        cat_name = row.category or "Uncategorized"
        colour = category_colours.get(cat_name, CATEGORY_COLOURS[i % len(CATEGORY_COLOURS)])
        # Ensure total is positive (amounts should already be positive for debits)
        total_amount = abs(float(row.total)) if row.total else 0.0
        result.append(
            CategorySpend(
                category=cat_name,
                total=round(total_amount, 2),
                count=int(row.cnt),
                color=colour,
            )
        )
    return result


# ──────────────────────────────────────────────
# Monthly trends
# ──────────────────────────────────────────────

def monthly_trends(db: Session, months: int = 12) -> List[MonthlyTrend]:
    """
    Return the last `months` months of income/expense/net data,
    reading from MonthlySummary if available, otherwise computing live.
    """
    now = datetime.utcnow()
    result: List[MonthlyTrend] = []

    for delta in range(months - 1, -1, -1):
        # Walk backwards from current month
        month = ((now.month - 1 - delta) % 12) + 1
        year = now.year + ((now.month - 1 - delta) // 12)

        summary = (
            db.query(models.MonthlySummary)
            .filter(
                models.MonthlySummary.year == year,
                models.MonthlySummary.month == month,
            )
            .first()
        )

        if summary:
            income = summary.total_income
            expenses = summary.total_expenses
            net = summary.net
        else:
            # Live computation
            start = datetime(year, month, 1)
            end_m = month + 1 if month < 12 else 1
            end_y = year if month < 12 else year + 1
            end = datetime(end_y, end_m, 1)
            txns = (
                db.query(models.Transaction)
                .filter(
                    models.Transaction.date >= start,
                    models.Transaction.date < end,
                )
                .all()
            )
            income = sum(t.amount for t in txns if t.transaction_type == "credit")
            expenses = abs(sum(t.amount for t in txns if t.transaction_type == "debit"))
            
            # Add jobs income only for the current month
            if year == now.year and month == now.month:
                jobs = db.query(models.Job).all()
                jobs_total = 0.0
                for j in jobs:
                    base = (j.hourly_wage or 0.0) * (j.expected_shifts or 0) * (j.hours_per_shift or 0.0)
                    ot = (j.hourly_wage or 0.0) * (j.ot1_5_hours or 0.0) * 1.5 + (j.hourly_wage or 0.0) * (j.ot2_hours or 0.0) * 2
                    jobs_total += base + ot
                income += jobs_total
            
            net = income - expenses

        result.append(
            MonthlyTrend(
                year=year,
                month=month,
                label=_month_label(year, month),
                income=round(income, 2),
                expenses=round(expenses, 2),
                net=round(net, 2),
            )
        )
    return result


# ──────────────────────────────────────────────
# Alert status
# ──────────────────────────────────────────────

def check_alerts(
    db: Session,
    year: int,
    month: int,
) -> List[dict]:
    """
    Compare actual monthly spend per category against user-defined limits.
    Returns a list of alert status dicts.
    """
    alerts = crud.get_alerts(db)
    if not alerts:
        return []

    start = datetime(year, month, 1)
    end_m = month + 1 if month < 12 else 1
    end_y = year if month < 12 else year + 1
    end = datetime(end_y, end_m, 1)

    # Actual spend per category this month
    rows = (
        db.query(
            models.Transaction.category,
            func.sum(models.Transaction.amount).label("total"),
        )
        .filter(
            models.Transaction.date >= start,
            models.Transaction.date < end,
            models.Transaction.transaction_type == "debit",
        )
        .group_by(models.Transaction.category)
        .all()
    )
    # Convert to positive values (debits should be positive amounts)
    actual: Dict[str, float] = {row.category or "Uncategorized": abs(float(row.total)) for row in rows}

    statuses = []
    for alert in alerts:
        if not alert.is_active:
            continue
        raw_spent = actual.get(alert.category, 0.0)
        spent = abs(raw_spent)
        pct = (spent / alert.monthly_limit * 100) if alert.monthly_limit > 0 else 0.0
        remaining = max(0, alert.monthly_limit - spent)
        statuses.append(
            {
                "category": alert.category,
                "limit": alert.monthly_limit,
                "spent": round(spent, 2),
                "remaining": round(remaining, 2),
                "percent": round(pct, 1),
                "exceeded": spent > alert.monthly_limit,
                "warning": spent > alert.monthly_limit * 0.8,
            }
        )
    return statuses


# ──────────────────────────────────────────────
# Dashboard summary
# ──────────────────────────────────────────────

def build_dashboard(db: Session) -> DashboardSummary:
    now = datetime.utcnow()
    year, month = now.year, now.month

    # Current month income/expenses
    start = datetime(year, month, 1)
    end_m = month + 1 if month < 12 else 1
    end_y = year if month < 12 else year + 1
    end = datetime(end_y, end_m, 1)

    txns = (
        db.query(models.Transaction)
        .filter(models.Transaction.date >= start, models.Transaction.date < end)
        .all()
    )
    income = sum(t.amount for t in txns if t.transaction_type == "credit")

    # Add jobs monthly income to dashboard income
    jobs = db.query(models.Job).all()
    jobs_total = 0.0
    for j in jobs:
        base = (j.hourly_wage or 0.0) * (j.expected_shifts or 0) * (j.hours_per_shift or 0.0)
        ot = (j.hourly_wage or 0.0) * (j.ot1_5_hours or 0.0) * 1.5 + (j.hourly_wage or 0.0) * (j.ot2_hours or 0.0) * 2
        jobs_total += base + ot
    income += jobs_total

    expenses = abs(sum(t.amount for t in txns if t.transaction_type == "debit"))  # Always positive
    net = income - expenses  # Correctly calculates income - expenses
    savings_rate = (net / income * 100) if income > 0 else 0.0

    breakdown = spending_by_category(db, year, month)
    trends = monthly_trends(db, months=12)
    alert_statuses = check_alerts(db, year, month)

    return DashboardSummary(
        current_month_income=round(income, 2),
        current_month_expenses=round(expenses, 2),
        current_month_net=round(net, 2),
        savings_rate=round(savings_rate, 2),
        category_breakdown=breakdown,
        monthly_trends=trends,
        alert_statuses=alert_statuses,
    )


# ──────────────────────────────────────────────
# 5-year projection
# ──────────────────────────────────────────────

def compute_projection(
    initial_balance: float,
    monthly_contribution: float,
    annual_return_pct: float,
    months: int = 60,
) -> ProjectionResponse:
    """
    Compound-monthly growth projection.

    Formula:
      FV = P*(1+r)^n + PMT * [((1+r)^n - 1) / r]
    where r = monthly rate, n = months.
    """
    monthly_rate = annual_return_pct / 100 / 12
    data_points: List[ProjectionDataPoint] = []

    now = datetime.utcnow()

    for n in range(months + 1):
        if monthly_rate == 0:
            balance = initial_balance + monthly_contribution * n
        else:
            balance = (
                initial_balance * ((1 + monthly_rate) ** n)
                + monthly_contribution * (((1 + monthly_rate) ** n - 1) / monthly_rate)
            )

        target_month = ((now.month - 1 + n) % 12) + 1
        target_year = now.year + ((now.month - 1 + n) // 12)
        label = _month_label(target_year, target_month)

        data_points.append(
            ProjectionDataPoint(month=n, label=label, balance=round(balance, 2))
        )

    return ProjectionResponse(
        initial_balance=initial_balance,
        monthly_contribution=monthly_contribution,
        annual_return_pct=annual_return_pct,
        months=months,
        data_points=data_points,
    )


# ──────────────────────────────────────────────
# Subscription detection
# ──────────────────────────────────────────────

def detect_subscriptions(db: Session) -> List[SubscriptionItem]:
    """
    Identify repeating charges:
    - Same description (exact, case-insensitive)
    - Amount within SUBSCRIPTION_AMOUNT_TOLERANCE % of mean amount
    - At least SUBSCRIPTION_MIN_OCCURRENCES occurrences
    """
    txns = (
        db.query(models.Transaction)
        .filter(models.Transaction.transaction_type == "debit")
        .order_by(models.Transaction.description, models.Transaction.date)
        .all()
    )

    # Group by lower-cased description
    groups: Dict[str, List[models.Transaction]] = defaultdict(list)
    for tx in txns:
        groups[tx.description.lower().strip()].append(tx)

    subscriptions: List[SubscriptionItem] = []

    for desc_key, txn_list in groups.items():
        if len(txn_list) < SUBSCRIPTION_MIN_OCCURRENCES:
            continue

        amounts = [t.amount for t in txn_list]
        mean_amount = sum(amounts) / len(amounts)

        # Check that all amounts are within tolerance of the mean
        all_similar = all(
            abs(a - mean_amount) / mean_amount <= SUBSCRIPTION_AMOUNT_TOLERANCE
            if mean_amount > 0
            else True
            for a in amounts
        )

        if not all_similar:
            continue

        last_tx = max(txn_list, key=lambda t: t.date)
        subscriptions.append(
            SubscriptionItem(
                description=txn_list[0].description,
                amount=round(mean_amount, 2),
                occurrences=len(txn_list),
                last_date=last_tx.date,
                category=last_tx.category,
            )
        )

    # Sort by amount desc
    subscriptions.sort(key=lambda s: s.amount, reverse=True)

    # Persist subscription flags to DB
    sub_descriptions = [s.description for s in subscriptions]
    if sub_descriptions:
        crud.mark_subscriptions(db, sub_descriptions)

    return subscriptions
