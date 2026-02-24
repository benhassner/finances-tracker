"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator


# ──────────────────────────────────────────────
# Category
# ──────────────────────────────────────────────

class CategoryBase(BaseModel):
    name: str
    color: Optional[str] = "#6366f1"
    icon: Optional[str] = "tag"
    budget_limit: Optional[float] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    budget_limit: Optional[float] = None


class CategoryOut(CategoryBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Transaction
# ──────────────────────────────────────────────

class TransactionBase(BaseModel):
    date: datetime
    description: str
    amount: float
    transaction_type: str          # 'debit' | 'credit'
    account_name: Optional[str] = ""
    category: Optional[str] = None
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    fingerprint: Optional[str] = None
    categorization_method: Optional[str] = "unset"


class TransactionUpdate(BaseModel):
    category: Optional[str] = None
    category_id: Optional[int] = None
    notes: Optional[str] = None
    categorization_method: Optional[str] = None


class TransactionOut(TransactionBase):
    id: int
    category_id: Optional[int] = None
    categorization_method: Optional[str] = None
    is_subscription: bool
    fingerprint: str
    imported_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[TransactionOut]


# ──────────────────────────────────────────────
# Rule
# ──────────────────────────────────────────────

class RuleBase(BaseModel):
    keyword: str
    category: str
    priority: Optional[int] = 5
    is_active: Optional[bool] = True


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    keyword: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class RuleOut(RuleBase):
    id: int
    category_id: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Monthly Summary
# ──────────────────────────────────────────────

class MonthlySummaryOut(BaseModel):
    id: int
    year: int
    month: int
    total_income: float
    total_expenses: float
    net: float
    savings_rate: float
    transaction_count: int
    computed_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Spending Alert
# ──────────────────────────────────────────────

class SpendingAlertBase(BaseModel):
    category: str
    monthly_limit: float
    is_active: Optional[bool] = True


class SpendingAlertCreate(SpendingAlertBase):
    pass


class SpendingAlertUpdate(BaseModel):
    monthly_limit: Optional[float] = None
    is_active: Optional[bool] = None


class SpendingAlertOut(SpendingAlertBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Jobs (Income entries)
# ──────────────────────────────────────────────

class JobBase(BaseModel):
    name: str
    hourly_wage: float
    expected_shifts: int
    hours_per_shift: float
    ot1_5_hours: float
    ot2_hours: float


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    name: Optional[str] = None
    hourly_wage: Optional[float] = None
    expected_shifts: Optional[int] = None
    hours_per_shift: Optional[float] = None
    ot1_5_hours: Optional[float] = None
    ot2_hours: Optional[float] = None


class JobOut(JobBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Analytics / Dashboard
# ──────────────────────────────────────────────

class CategorySpend(BaseModel):
    category: str
    total: float
    count: int
    color: Optional[str] = "#6366f1"


class MonthlyTrend(BaseModel):
    year: int
    month: int
    label: str          # e.g. "Jan 2025"
    income: float
    expenses: float
    net: float


class DashboardSummary(BaseModel):
    current_month_income: float
    current_month_expenses: float
    current_month_net: float
    savings_rate: float
    category_breakdown: List[CategorySpend]
    monthly_trends: List[MonthlyTrend]
    alert_statuses: List[dict]


class ProjectionDataPoint(BaseModel):
    month: int          # months from now (0 = today)
    label: str          # e.g. "Jan 2026"
    balance: float


class ProjectionResponse(BaseModel):
    initial_balance: float
    monthly_contribution: float
    annual_return_pct: float
    months: int
    data_points: List[ProjectionDataPoint]


class SubscriptionItem(BaseModel):
    description: str
    amount: float
    occurrences: int
    last_date: datetime
    category: Optional[str] = None


class ImportResponse(BaseModel):
    imported: int
    duplicates: int
    errors: int
    messages: List[str]


class RetrainResponse(BaseModel):
    status: str
    training_samples: int
    accuracy: Optional[float] = None
    message: str
