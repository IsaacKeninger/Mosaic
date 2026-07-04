"""POST /sync/{userId} — pull latest transactions from Plaid, store in DynamoDB."""
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.db import users_table
from backend.plaid.sync import store_transactions, sync_transactions

router = APIRouter()


@router.post("/{user_id}")
def sync_user(user_id: str) -> dict:
    user = users_table().get_item(Key={"userId": user_id}).get("Item")
    if user is None or "plaidAccessToken" not in user:
        raise HTTPException(
            status_code=404,
            detail=f"No Plaid access token on file for {user_id}. Run scripts/seed_dynamo.py first.",
        )

    transactions = sync_transactions(user["plaidAccessToken"], user_id)
    store_transactions(transactions)

    last_synced = datetime.now(timezone.utc).isoformat()
    users_table().update_item(
        Key={"userId": user_id},
        UpdateExpression="SET lastSynced = :ts",
        ExpressionAttributeValues={":ts": last_synced},
    )

    return {"userId": user_id, "transactionsSynced": len(transactions), "lastSynced": last_synced}
