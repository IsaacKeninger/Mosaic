"""Plaid SDK client initialization (Sandbox environment)."""
import os

import plaid
from plaid.api import plaid_api


def get_plaid_client() -> plaid_api.PlaidApi:
    """Build a Plaid API client from environment credentials."""
    env_map = {
        "sandbox": plaid.Environment.Sandbox,
        "development": plaid.Environment.Development,
        "production": plaid.Environment.Production,
    }
    host = env_map[os.environ.get("PLAID_ENV", "sandbox")]

    configuration = plaid.Configuration(
        host=host,
        api_key={
            "clientId": os.environ["PLAID_CLIENT_ID"],
            "secret": os.environ["PLAID_SECRET"],
        },
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)
