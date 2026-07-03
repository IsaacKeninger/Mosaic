"""Feature engineering pipeline: raw transactions -> per-user feature vector."""
import pandas as pd

from backend.features.constants import FEATURE_COLUMNS


def engineer_features(transactions: pd.DataFrame) -> pd.Series:
    """Compute the full feature vector for a single user's transactions.

    Expects a DataFrame with columns matching the mosaic-transactions schema
    (amount, normalized_merchant, category, date, is_recurring).

    TODO: implement each feature described in CLAUDE.md's Feature Engineering
    Pipeline section (spending distribution, behavioral, temporal features).
    """
    raise NotImplementedError


def engineer_features_batch(transactions_by_user: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Run engineer_features for every user and assemble a feature matrix."""
    rows = {
        user_id: engineer_features(txns)
        for user_id, txns in transactions_by_user.items()
    }
    return pd.DataFrame.from_dict(rows, orient="index", columns=FEATURE_COLUMNS)
