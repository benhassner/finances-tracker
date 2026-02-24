"""
SQLAlchemy ORM models for the finance tracker.
Compatible with both SQLite (local development) and PostgreSQL (production).
"""
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    color = Column(String(7), default="#6366f1")  # hex colour for UI
    icon = Column(String(50), default="tag")
    budget_limit = Column(Float, nullable=True)  # monthly budget cap
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="category_obj")
    rules = relationship("Rule", back_populates="category_obj")

    def __repr__(self):
        return f"<Category id={self.id} name={self.name!r}>"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(10), nullable=False)  # 'debit' | 'credit'
    account_name = Column(String(150), nullable=False, default="")
    category = Column(String(100), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    # Track how category was assigned
    categorization_method = Column(String(20), default="unset")  # rule | ml | manual | unset
    is_subscription = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    # Deduplication fingerprint
    fingerprint = Column(String(256), unique=True, nullable=False, index=True)
    imported_at = Column(DateTime, default=datetime.utcnow)

    category_obj = relationship("Category", back_populates="transactions")

    __table_args__ = (
        Index("ix_transactions_date_category", "date", "category"),
        Index("ix_transactions_type_date", "transaction_type", "date"),
    )

    def __repr__(self):
        return f"<Transaction id={self.id} date={self.date} amount={self.amount}>"


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(200), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    priority = Column(Integer, default=5)  # higher wins when multiple rules match
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    category_obj = relationship("Category", back_populates="rules")

    __table_args__ = (
        UniqueConstraint("keyword", "category", name="uq_rule_keyword_category"),
        Index("ix_rules_active_priority", "is_active", "priority"),
    )

    def __repr__(self):
        return f"<Rule id={self.id} keyword={self.keyword!r} → {self.category!r}>"


class MonthlySummary(Base):
    """
    Pre-computed monthly aggregates — refreshed on import and on demand.
    Speeds up dashboard queries dramatically for large datasets.
    """
    __tablename__ = "monthly_summaries"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    total_income = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)
    net = Column(Float, default=0.0)
    savings_rate = Column(Float, default=0.0)  # percentage 0-100
    transaction_count = Column(Integer, default=0)
    computed_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("year", "month", name="uq_monthly_summary_ym"),
        Index("ix_monthly_summary_year_month", "year", "month"),
    )

    def __repr__(self):
        return f"<MonthlySummary {self.year}-{self.month:02d} net={self.net}>"


class SpendingAlert(Base):
    """User-defined budget alerts per category."""
    __tablename__ = "spending_alerts"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False, unique=True, index=True)
    monthly_limit = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SpendingAlert category={self.category!r} limit={self.monthly_limit}>"


class Job(Base):
    """User-defined job entries for expected monthly income."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    hourly_wage = Column(Float, nullable=False, default=0.0)
    expected_shifts = Column(Integer, nullable=False, default=0)
    hours_per_shift = Column(Float, nullable=False, default=0.0)
    ot1_5_hours = Column(Float, nullable=False, default=0.0)
    ot2_hours = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Job id={self.id} name={self.name!r}>"


class GroupedSpendingAlert(Base):
    """Grouped alerts that track multiple categories under a single name."""
    __tablename__ = "grouped_spending_alerts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    categories_json = Column(Text, nullable=False, default="[]")
    monthly_limit = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Convenience property for schemas
    @property
    def categories(self):  # type: ignore
        import json
        try:
            data = json.loads(self.categories_json or "[]")
            return data if isinstance(data, list) else []
        except Exception:
            return []

    @categories.setter
    def categories(self, value):  # type: ignore
        import json
        self.categories_json = json.dumps(value or [])

    def __repr__(self):
        return f"<GroupedSpendingAlert name={self.name!r} limit={self.monthly_limit}>"
