"""Spending category mappings used across feature engineering."""

# Maps our normalized categories to Plaid's personal_finance_category values.
CATEGORY_MAP: dict[str, list[str]] = {
    "food_dining": ["FOOD_AND_DRINK"],
    "shopping": ["GENERAL_MERCHANDISE"],
    "entertainment": ["ENTERTAINMENT"],
    "travel": ["TRAVEL"],
    "health_fitness": ["MEDICAL", "PERSONAL_CARE"],
    "subscriptions": ["ENTERTAINMENT", "GENERAL_SERVICES"],
    "groceries": ["FOOD_AND_DRINK"],
}

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
