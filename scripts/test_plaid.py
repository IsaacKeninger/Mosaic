"""Verify Plaid Sandbox credentials and connectivity end-to-end.
Usage: python scripts/test_plaid.py
"""
from dotenv import load_dotenv

from backend.plaid.sync import create_sandbox_public_token, exchange_public_token, sync_transactions

load_dotenv()

def main() -> None:
    public_token = create_sandbox_public_token("user_good", "pass_good")
    print(f"Public token: {public_token}")

    access_token = exchange_public_token(public_token)
    print(f"Access token: {access_token}")

    transactions = sync_transactions(access_token, user_id="user_good")
    print(f"Pulled {len(transactions)} transactions. Sample:")
    for txn in transactions[:5]:
        print(f"  {txn.date}  {txn.normalized_merchant:<25}  {txn.amount:>8.2f}  {txn.category}")

if __name__ == "__main__":
    main()
