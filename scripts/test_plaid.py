"""Verify Plaid Sandbox credentials and connectivity.

Usage: python scripts/test_plaid.py
"""
from dotenv import load_dotenv

from backend.plaid.client import get_plaid_client

load_dotenv()


def main() -> None:
    client = get_plaid_client()
    # TODO: create a sandbox public token for user_good, exchange it, and
    # print back a sample of transactions to confirm end-to-end connectivity.
    print("Plaid client initialized:", client)


if __name__ == "__main__":
    main()
