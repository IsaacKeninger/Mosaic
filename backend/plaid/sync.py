"""Pull transactions from Plaid and normalize them for storage."""
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.sandbox_public_token_create_request_options import (
    SandboxPublicTokenCreateRequestOptions,
)
from plaid.model.transactions_sync_request import TransactionsSyncRequest

from backend.features.normalize import normalize_merchant
from backend.plaid.client import get_plaid_client
from backend.plaid.models import Transaction

# First Platypus Bank — Plaid's default Sandbox institution.
SANDBOX_INSTITUTION_ID = "ins_109508"

def create_sandbox_public_token(username: str, password: str) -> str:
    """Exchange Plaid Sandbox test credentials for a public token."""
    client = get_plaid_client()
    request = SandboxPublicTokenCreateRequest(
        institution_id=SANDBOX_INSTITUTION_ID,
        initial_products=[Products("transactions")],
        options=SandboxPublicTokenCreateRequestOptions(
            override_username=username,
            override_password=password,
        ),
    )
    response = client.sandbox_public_token_create(request)
    return response.public_token

def exchange_public_token(public_token: str) -> str:
    """Exchange a public token for a long-lived access token."""
    client = get_plaid_client()
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    return response.access_token

def sync_transactions(access_token: str, user_id: str) -> list[Transaction]:
    """Pull and normalize all transactions for a user via /transactions/sync.

    Paginates using the cursor Plaid returns until has_more is False. Only
    added transactions are handled here — modified/removed handling can be
    layered on once this is backed by real storage instead of a one-shot pull.
    """
    client = get_plaid_client()
    transactions: list[Transaction] = []
    cursor: str | None = None
    has_more = True

    while has_more:
        request = TransactionsSyncRequest(access_token=access_token, cursor=cursor)
        response = client.transactions_sync(request)

        for txn in response.added:
            raw_name = txn.merchant_name or txn.name
            category = (
                txn.personal_finance_category.primary
                if txn.personal_finance_category
                else None
            )
            transactions.append(
                Transaction(
                    user_id=user_id,
                    transaction_id=txn.transaction_id,
                    amount=txn.amount,
                    merchant_name=txn.merchant_name,
                    normalized_merchant=normalize_merchant(raw_name) if raw_name else None,
                    category=category,
                    date=txn.date,
                    # Plaid's /transactions/sync doesn't flag recurring
                    # transactions directly; recurring detection needs its
                    # own heuristic in features/engineer.py.
                    is_recurring=False,
                )
            )

        cursor = response.next_cursor
        has_more = response.has_more

    return transactions