"""Run model training end-to-end and upload artifacts to S3.

Usage: python scripts/train_model.py
"""
from dotenv import load_dotenv

from backend.ml.train import train

load_dotenv()

if __name__ == "__main__":
    train()
