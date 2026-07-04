"""Spending category mappings used across feature engineering.

Plaid's personal_finance_category has two levels: a coarse `primary` (e.g.
FOOD_AND_DRINK) and a finer `detailed` (e.g. FOOD_AND_DRINK_GROCERIES vs.
FOOD_AND_DRINK_RESTAURANT). Groceries and dining share the same primary
category, so that split can only be made using `detailed`.
"""

PRIMARY_CATEGORY_TO_BUCKET: dict[str, str] = {
    "FOOD_AND_DRINK": "food_dining",
    "GENERAL_MERCHANDISE": "shopping",
    "ENTERTAINMENT": "entertainment",
    "TRAVEL": "travel",
    "TRANSPORTATION": "travel",
    "MEDICAL": "health_fitness",
    "PERSONAL_CARE": "health_fitness",
}

GROCERY_DETAILED_CATEGORY = "FOOD_AND_DRINK_GROCERIES"

# Categories eligible to count toward pct_subscriptions when also flagged as
# a recurring transaction (see features/engineer.py's recurring detector).
SUBSCRIPTION_ELIGIBLE_BUCKETS = {"entertainment"}


def bucket_for_transaction(primary: str | None, detailed: str | None) -> str:
    """Map a Plaid category pair to one of our spending buckets, or 'other'."""
    if detailed == GROCERY_DETAILED_CATEGORY:
        return "groceries"
    return PRIMARY_CATEGORY_TO_BUCKET.get(primary or "", "other")


FEATURE_COLUMNS: list[str] = [
    "pct_food_dining",
    "pct_shopping",
    "pct_entertainment",
    "pct_travel",
    "pct_health_fitness",
    "pct_subscriptions",
    "pct_groceries",
    "avg_transaction_size",
    "spending_volatility",
    "weekend_spend_ratio",
    "late_night_ratio",
    "unique_merchant_count",
    "recurring_ratio",
    "savings_rate",
    "month_end_spike",
    "paycheck_to_paycheck",
    "spending_trend",
]
