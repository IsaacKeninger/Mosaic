"""Lambda handler: API Gateway POST /classify/{userId}. Runtime: Python 3.12."""
from backend.features.engineer import engineer_features


def handler(event: dict, context) -> dict:
    user_id = event["pathParameters"]["userId"]
    raise NotImplementedError
