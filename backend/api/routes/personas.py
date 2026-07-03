"""GET /persona/{userId} and POST /persona/generate/{clusterId}."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/{user_id}")
def get_persona(user_id: str) -> dict:
    raise NotImplementedError


@router.post("/generate/{cluster_id}")
def generate_persona(cluster_id: int) -> dict:
    raise NotImplementedError
