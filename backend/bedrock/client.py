"""Amazon Bedrock client initialization."""
import os

import boto3


def get_bedrock_client():
    return boto3.client(
        "bedrock-runtime",
        region_name=os.environ.get("BEDROCK_REGION", "us-east-1"),
    )
