"""Lambda handler: API Gateway POST /persona/generate/{clusterId}. Runtime: Python 3.12."""
from backend.bedrock.persona import generate_persona


def handler(event: dict, context) -> dict:
    cluster_id = event["pathParameters"]["clusterId"]
    raise NotImplementedError
