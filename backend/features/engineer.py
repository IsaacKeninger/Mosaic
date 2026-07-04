"""Feature engineering pipeline: raw transactions -> per-user feature vector.

Expects a DataFrame per user with columns matching the mosaic-transactions
schema: amount, normalized_merchant, category, category_detailed, date.
Plaid convention: amount > 0 is money leaving the account (spend), amount < 0
is money coming in (income/deposits/refunds).
"""
import calendar

import numpy as np
import pandas as pd

from backend.features.constants import (
    FEATURE_COLUMNS,
    SUBSCRIPTION_ELIGIBLE_BUCKETS,
    bucket_for_transaction,
)

# (period_days, tolerance_days) buckets a recurring charge is allowed to fall
# into — covers weekly, biweekly, and monthly billing cycles.
_RECURRING_PERIODS = [(7, 2), (14, 3), (30, 5)]
_RECURRING_AMOUNT_CV_THRESHOLD = 0.15


def _detect_recurring(df: pd.DataFrame) -> pd.Series:
    """Flag transactions whose merchant repeats at a roughly fixed interval
    with a consistent amount (weekly/biweekly/monthly, low amount variance).

    Plaid's transaction data doesn't mark recurring charges directly, so this
    heuristic stands in for it.
    """
    is_recurring = pd.Series(False, index=df.index)

    for _, group in df.groupby("normalized_merchant"):
        if len(group) < 2:
            continue
        ordered = group.sort_values("date")
        gaps = ordered["date"].diff().dt.days.dropna()
        if gaps.empty:
            continue

        mean_gap = gaps.mean()
        mean_amount = ordered["amount"].mean()
        amount_cv = ordered["amount"].std() / mean_amount if mean_amount else np.inf

        is_periodic = any(abs(mean_gap - period) <= tol for period, tol in _RECURRING_PERIODS)
        if is_periodic and amount_cv < _RECURRING_AMOUNT_CV_THRESHOLD:
            is_recurring.loc[ordered.index] = True

    return is_recurring


def _month_end_spike(spend: pd.DataFrame) -> float:
    """Ratio of last-5-days spend vs. the expected 5-day share of the month,
    averaged across all months present. >1 means spend skews toward month end."""
    ratios = []
    for period, group in spend.groupby(spend["date"].dt.to_period("M")):
        days_in_month = calendar.monthrange(period.year, period.month)[1]
        month_total = group["amount"].sum()
        if month_total <= 0:
            continue
        last_5_start_day = days_in_month - 4
        last_5_spend = group.loc[group["date"].dt.day >= last_5_start_day, "amount"].sum()
        expected_5_day_share = month_total / days_in_month * 5
        ratios.append(last_5_spend / expected_5_day_share)

    return float(np.mean(ratios)) if ratios else 0.0


def engineer_features(transactions: pd.DataFrame) -> pd.Series:
    """Compute the full feature vector for a single user's transactions."""
    if transactions.empty:
        return pd.Series(0.0, index=FEATURE_COLUMNS)

    df = transactions.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["is_recurring"] = _detect_recurring(df)
    df["bucket"] = [
        bucket_for_transaction(p, d) for p, d in zip(df["category"], df["category_detailed"])
    ]

    spend = df[df["amount"] > 0]
    income = df[df["amount"] < 0]

    total_spend = spend["amount"].sum()
    total_income = -income["amount"].sum()

    def pct(bucket: str) -> float:
        if total_spend <= 0:
            return 0.0
        return spend.loc[spend["bucket"] == bucket, "amount"].sum() / total_spend

    pct_subscriptions = 0.0
    if total_spend > 0:
        subscription_spend = spend.loc[
            spend["is_recurring"] & spend["bucket"].isin(SUBSCRIPTION_ELIGIBLE_BUCKETS),
            "amount",
        ].sum()
        pct_subscriptions = subscription_spend / total_spend

    monthly_totals = spend.groupby(spend["date"].dt.to_period("M"))["amount"].sum()
    spending_volatility = float(monthly_totals.std()) if len(monthly_totals) >= 2 else 0.0

    weekend_spend = spend.loc[spend["date"].dt.dayofweek >= 5, "amount"].sum()
    weekend_spend_ratio = weekend_spend / total_spend if total_spend > 0 else 0.0

    monthly_unique_merchants = spend.groupby(spend["date"].dt.to_period("M"))[
        "normalized_merchant"
    ].nunique()
    unique_merchant_count = float(monthly_unique_merchants.mean()) if len(monthly_unique_merchants) else 0.0

    recurring_ratio = df["is_recurring"].mean() if len(df) else 0.0

    savings_rate = (total_income - total_spend) / total_income if total_income > 0 else 0.0

    month_end_spike = _month_end_spike(spend)

    # Proxy only: real detection needs account balance data (Plaid's Balance
    # product), which this pipeline doesn't pull. Flags users who spend
    # nearly all of their income as a stand-in for running low before payday.
    paycheck_to_paycheck = bool(savings_rate < 0.05)

    spending_trend = 0.0
    if len(monthly_totals) >= 2:
        x = np.arange(len(monthly_totals))
        spending_trend = float(np.polyfit(x, monthly_totals.values, 1)[0])

    values = {
        "pct_food_dining": pct("food_dining"),
        "pct_shopping": pct("shopping"),
        "pct_entertainment": pct("entertainment"),
        "pct_travel": pct("travel"),
        "pct_health_fitness": pct("health_fitness"),
        "pct_subscriptions": pct_subscriptions,
        "pct_groceries": pct("groceries"),
        "avg_transaction_size": float(spend["amount"].mean()) if len(spend) else 0.0,
        "spending_volatility": spending_volatility,
        "weekend_spend_ratio": weekend_spend_ratio,
        # Plaid's posted transactions carry a date but not a time of day, so
        # late-night detection isn't computable from this data source.
        "late_night_ratio": 0.0,
        "unique_merchant_count": unique_merchant_count,
        "recurring_ratio": recurring_ratio,
        "savings_rate": savings_rate,
        "month_end_spike": month_end_spike,
        "paycheck_to_paycheck": paycheck_to_paycheck,
        "spending_trend": spending_trend,
    }

    return pd.Series(values, index=FEATURE_COLUMNS)


def engineer_features_batch(transactions_by_user: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Run engineer_features for every user and assemble a feature matrix."""
    rows = {
        user_id: engineer_features(txns)
        for user_id, txns in transactions_by_user.items()
    }
    return pd.DataFrame.from_dict(rows, orient="index", columns=FEATURE_COLUMNS)
