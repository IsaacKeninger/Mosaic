"""Pull transactions from Plaid and normalize them for storage."""
from backend.plaid.client import get_plaid_client
from backend.plaid.models import Transaction


def create_sandbox_public_token(username: str, password: str) -> str:
    """Exchange Plaid Sandbox test credentials for a public token.

    TODO: call /sandbox/public_token/create with institution_id ins_109508
    (First Platypus Bank) and the requested products.
    """
    raise NotImplementedError


def exchange_public_token(public_token: str) -> str:
    """Exchange a public token for a long-lived access token.

    TODO: call /item/public_token/exchange
    """
    raise NotImplementedError


def sync_transactions(access_token: str) -> list[Transaction]:
    """Pull and normalize transactions for a user via /transactions/sync.

    TODO: paginate through /transactions/sync, map raw Plaid transactions
    to the Transaction model, and normalize merchant names.
    """
    raise NotImplementedError
