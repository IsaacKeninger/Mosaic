"""Shared API Gateway proxy-response glue for the Lambda handlers.

Each Lambda calls the identical function the FastAPI routes use locally, so
there is exactly one implementation of each endpoint's business logic.
"""
import json

from fastapi import HTTPException

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
}


def invoke(fn, *args, **kwargs) -> dict:
    try:
        result = fn(*args, **kwargs)
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(result, default=str)}
    except HTTPException as e:
        return {"statusCode": e.status_code, "headers": CORS_HEADERS, "body": json.dumps({"detail": e.detail})}
