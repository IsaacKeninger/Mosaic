"""POST /classify/{userId} — feature engineer + assign cluster."""
from decimal import Decimal

from fastapi import APIRouter, HTTPException

from backend.db import users_table
from backend.features.constants import FEATURE_COLUMNS
from backend.features.engineer import engineer_features
from backend.ml.predict import classify_feature_vector
from backend.plaid.sync import load_transactions

router = APIRouter()


@router.post("/{user_id}")
def classify_user(user_id: str) -> dict:
    transactions = load_transactions(user_id)
    if transactions.empty:
        raise HTTPException(status_code=404, detail=f"No synced transactions for {user_id}. Sync first.")

    features = engineer_features(transactions)
    cluster_id, (x, y) = classify_feature_vector(features[FEATURE_COLUMNS].to_numpy())
    persona_id = f"persona-{cluster_id}"

    users_table().update_item(
        Key={"userId": user_id},
        UpdateExpression="SET clusterId = :c, personaId = :p, featureVector = :f, pcaCoordinates = :pca",
        ExpressionAttributeValues={
            ":c": cluster_id,
            ":p": persona_id,
            ":f": {k: Decimal(str(v)) for k, v in features.items()},
            ":pca": {"x": Decimal(str(x)), "y": Decimal(str(y))},
        },
    )

    return {
        "userId": user_id,
        "clusterId": cluster_id,
        "personaId": persona_id,
        "pcaCoordinates": {"x": x, "y": y},
    }
