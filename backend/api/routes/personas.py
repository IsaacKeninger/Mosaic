"""GET /persona/{userId}, GET /persona/details/{personaId}, GET /persona/scatter,
and POST /persona/generate/{clusterId}."""
from fastapi import APIRouter, HTTPException

from backend.bedrock.persona import generate_and_store_persona
from backend.db import list_user_ids, personas_table, users_table

router = APIRouter()


@router.get("/{user_id}")
def get_persona(user_id: str) -> dict:
    user = users_table().get_item(Key={"userId": user_id}).get("Item")
    if user is None:
        raise HTTPException(status_code=404, detail=f"Unknown user {user_id}")
    # plaidAccessToken is a bearer credential for the user's bank data — never
    # let it leave the backend, even though it lives alongside these fields
    # in the same DynamoDB item.
    user.pop("plaidAccessToken", None)
    return user


@router.get("/details/{persona_id}")
def get_persona_details(persona_id: str) -> dict:
    persona = personas_table().get_item(Key={"personaId": persona_id}).get("Item")
    if persona is None:
        raise HTTPException(status_code=404, detail=f"Unknown persona {persona_id}")
    return persona


@router.get("/scatter/all")
def get_all_scatter_points() -> list[dict]:
    """Feeds the PersonaScatter dashboard component: every user's PCA point,
    colored by clusterId. Not one of CLAUDE.md's four named Lambdas, but the
    frontend component needs a way to fetch the full population."""
    users = users_table()
    points = []
    for user_id in list_user_ids():
        item = users.get_item(Key={"userId": user_id}).get("Item")
        if item and "pcaCoordinates" in item:
            points.append(
                {
                    "userId": user_id,
                    "clusterId": item.get("clusterId"),
                    "x": float(item["pcaCoordinates"]["x"]),
                    "y": float(item["pcaCoordinates"]["y"]),
                }
            )
    return points


@router.post("/generate/{cluster_id}")
def generate_persona_route(cluster_id: int) -> dict:
    persona_id = f"persona-{cluster_id}"
    try:
        persona = generate_and_store_persona(persona_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"personaId": persona_id, **persona}
