"""Lambda handler: API Gateway GET /persona/{userId}. Runtime: Python 3.12."""


def handler(event: dict, context) -> dict:
    user_id = event["pathParameters"]["userId"]
    raise NotImplementedError
