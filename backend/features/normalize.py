"""Merchant name normalization for noisy raw Plaid merchant strings."""
from rapidfuzz import fuzz, process

# Seed list of canonical merchants; extend as new noisy names are discovered.
CANONICAL_MERCHANTS: list[str] = [
    "Whole Foods",
    "McDonald's",
    "Starbucks",
    "Amazon",
    "Target",
    "Walmart",
]


def strip_store_number(raw_name: str) -> str:
    """Strip trailing store numbers, e.g. 'WHOLEFDS #1234' -> 'WHOLEFDS'."""
    import re

    return re.sub(r"\s*#\d+$", "", raw_name).strip()


def normalize_merchant(raw_name: str, threshold: int = 85) -> str:
    """Map a raw Plaid merchant name to a canonical merchant name.

    TODO: expand CANONICAL_MERCHANTS and abbreviation handling as real
    Plaid sandbox data is observed.
    """
    cleaned = strip_store_number(raw_name)
    match = process.extractOne(cleaned, CANONICAL_MERCHANTS, scorer=fuzz.WRatio)
    if match and match[1] >= threshold:
        return match[0]
    return cleaned
