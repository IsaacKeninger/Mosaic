"""Lambda handler: API Gateway POST /classify/{userId}. Runtime: Python 3.12."""
from backend.api.routes.classify import classify_user
from backend.lambdas._common import invoke


def handler(event: dict, context) -> dict:
    return invoke(classify_user, event["pathParameters"]["userId"])
