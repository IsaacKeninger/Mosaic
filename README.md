# Mosaic — Financial Persona Categorizer

Mosaic pulls transaction data from the Plaid Sandbox API, engineers behavioral
spending features, runs unsupervised ML clustering to discover natural financial
personas, and uses Amazon Bedrock to generate natural language persona descriptions.
Results are surfaced through a Next.js dashboard deployed serverlessly on AWS.

See [CLAUDE.md](CLAUDE.md) for full architecture, schema, and development phase details.

## Stack

Plaid · pandas/scikit-learn · Amazon Bedrock · FastAPI · AWS Lambda/API Gateway/DynamoDB/S3 · CDK · Next.js

## Getting Started

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload

# Infrastructure
cd infrastructure
npm install
cdk bootstrap
cdk deploy

# Frontend
cd frontend
npm install
npm run dev
```

Copy `.env.example` to `.env` and fill in Plaid + AWS credentials before running anything.

## Status

Early scaffold — see the Development Phases checklist in [CLAUDE.md](CLAUDE.md) for progress.
