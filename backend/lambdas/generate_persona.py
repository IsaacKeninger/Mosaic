"""Lambda handler: API Gateway POST /persona/generate/{clusterId}. Runtime: Python 3.12."""
from backend.api.routes.personas import generate_persona_route
from backend.lambdas._common import invoke


def handler(event: dict, context) -> dict:
    return invoke(generate_persona_route, int(event["pathParameters"]["clusterId"]))
