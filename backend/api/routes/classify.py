"""POST /classify/{userId} — feature engineer + assign cluster."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/{user_id}")
def classify_user(user_id: str) -> dict:
    raise NotImplementedError
