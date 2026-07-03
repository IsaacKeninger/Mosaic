"""Lambda handler: API Gateway POST /sync/{userId}. Runtime: Python 3.12."""
from backend.plaid.sync import sync_transactions


def handler(event: dict, context) -> dict:
    user_id = event["pathParameters"]["userId"]
    raise NotImplementedError
