"""Shared DynamoDB table access. Table names come from environment variables
set by CDK outputs (see .env.example)."""
import os

import boto3

_dynamodb = None


def _resource():
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    return _dynamodb


def users_table():
    return _resource().Table(os.environ["DYNAMO_USERS_TABLE"])


def personas_table():
    return _resource().Table(os.environ["DYNAMO_PERSONAS_TABLE"])


def transactions_table():
    return _resource().Table(os.environ["DYNAMO_TRANSACTIONS_TABLE"])


def list_user_ids() -> list[str]:
    """Scan mosaic-users for every known userId (small table, scan is fine)."""
    table = users_table()
    user_ids = []
    response = table.scan(ProjectionExpression="userId")
    user_ids.extend(item["userId"] for item in response["Items"])
    while "LastEvaluatedKey" in response:
        response = table.scan(ProjectionExpression="userId", ExclusiveStartKey=response["LastEvaluatedKey"])
        user_ids.extend(item["userId"] for item in response["Items"])
    return user_ids
