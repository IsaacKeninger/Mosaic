"""Lambda handler: API Gateway POST /sync/{userId}. Runtime: Python 3.12."""
from backend.api.routes.plaid import sync_user
from backend.lambdas._common import invoke


def handler(event: dict, context) -> dict:
    return invoke(sync_user, event["pathParameters"]["userId"])
