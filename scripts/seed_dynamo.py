"""Seed DynamoDB tables with initial sandbox users for local dev / demo.

Usage: python scripts/seed_dynamo.py
"""
import os

import boto3
from dotenv import load_dotenv

load_dotenv()

SANDBOX_USERS = [
    {"username": "user_good", "password": "pass_good", "profile": "Good standing, regular income"},
    {"username": "user_custom", "password": "pass_good", "profile": "Customizable transactions"},
    {"username": "user_employee", "password": "pass_good", "profile": "Salaried employee profile"},
]


def main() -> None:
    dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    users_table = dynamodb.Table(os.environ["DYNAMO_USERS_TABLE"])

    # TODO: for each sandbox user, create a Plaid public token, exchange it,
    # and write the resulting access token + userId into mosaic-users.
    for user in SANDBOX_USERS:
        print(f"TODO: seed {user['username']}")


if __name__ == "__main__":
    main()
