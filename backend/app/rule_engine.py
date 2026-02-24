"""
Rule-based categorisation engine.

Rules are stored in the DB (table: rules) and sorted by priority descending.
The first matching rule wins.  Matching is case-insensitive substring search
against the transaction description.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app import models


def apply_rules(description: str, rules: List[models.Rule]) -> Optional[str]:
    """
    Match `description` against the supplied rule list (already sorted by
    priority desc).  Returns the category name of the first match or None.
    """
    lower_desc = description.lower()
    for rule in rules:
        if not rule.is_active:
            continue
        if rule.keyword.lower() in lower_desc:
            return rule.category
    return None


def categorise_transaction(
    description: str,
    db: Session,
    *,
    cached_rules: Optional[List[models.Rule]] = None,
) -> Optional[str]:
    """
    Convenience wrapper that fetches rules from the DB (or uses a pre-fetched
    cache) and applies them to a single description.

    Pass `cached_rules` when processing a batch to avoid N+1 DB queries.
    """
    rules = cached_rules if cached_rules is not None else _fetch_sorted_rules(db)
    return apply_rules(description, rules)


def _fetch_sorted_rules(db: Session) -> List[models.Rule]:
    from sqlalchemy import desc, asc
    return (
        db.query(models.Rule)
        .filter(models.Rule.is_active == True)
        .order_by(desc(models.Rule.priority), asc(models.Rule.keyword))
        .all()
    )


def batch_categorise(
    transactions: List[models.Transaction],
    db: Session,
) -> int:
    """
    Apply rules to every *uncategorised* transaction in `transactions`.
    Returns the number of transactions that were categorised.
    """
    from sqlalchemy import desc, asc
    from app.crud import get_category_by_name

    rules = _fetch_sorted_rules(db)
    updated = 0

    for tx in transactions:
        # Skip if already manually categorised
        if tx.categorization_method == "manual":
            continue

        category = apply_rules(tx.description, rules)
        if category:
            tx.category = category
            tx.categorization_method = "rule"
            cat_obj = get_category_by_name(db, category)
            tx.category_id = cat_obj.id if cat_obj else None
            updated += 1

    db.commit()
    return updated
