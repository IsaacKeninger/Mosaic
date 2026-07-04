"""Lambda handler: API Gateway GET /persona/{userId}. Runtime: Python 3.12."""
from backend.api.routes.personas import get_persona
from backend.lambdas._common import invoke


def handler(event: dict, context) -> dict:
    return invoke(get_persona, event["pathParameters"]["userId"])
