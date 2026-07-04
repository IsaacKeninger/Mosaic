"""Pydantic models for normalized Plaid data."""
from datetime import date

from pydantic import BaseModel


class Transaction(BaseModel):
    user_id: str
    transaction_id: str
    amount: float
    merchant_name: str | None = None
    normalized_merchant: str | None = None
    category: str | None = None
    category_detailed: str | None = None
    date: date
    is_recurring: bool = False


class SandboxUser(BaseModel):
    username: str
    password: str
    profile: str
