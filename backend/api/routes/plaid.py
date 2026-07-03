"""POST /sync/{userId} — pull latest transactions from Plaid, store in DynamoDB."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/{user_id}")
def sync_user(user_id: str) -> dict:
    raise NotImplementedError
