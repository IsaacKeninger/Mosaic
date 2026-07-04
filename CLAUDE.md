# Mosaic Financial Persona Categorizer — CLAUDE.md

## Project Overview

**Mosaic** is a financial persona classifier that pulls real transaction data from
the Plaid Sandbox API, engineers behavioral features, runs unsupervised ML clustering
to discover natural spending personas, and uses Amazon Bedrock to generate rich natural
language persona descriptions. Results are surfaced through a Next.js dashboard deployed
serverlessly on AWS.

**Developer:** Isaac Keninger
**Goal:** Resume project targeting fintech/tech internships for Summer 2027 recruiting cycle.
Showcase ML, Plaid API, AWS infrastructure (Lambda, DynamoDB, CDK), and Bedrock in one
cohesive project.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Transaction Data | Plaid Python SDK (Sandbox) |
| Feature Engineering | Python, pandas, numpy |
| ML Clustering | scikit-learn (K-Means, DBSCAN), PCA |
| Persona Generation | Amazon Bedrock (Claude claude-sonnet-4-6) |
| Backend API | FastAPI |
| Serverless Deployment | AWS Lambda + API Gateway |
| Database | AWS DynamoDB |
| Model Storage | AWS S3 |
| Infrastructure as Code | AWS CDK (TypeScript) |
| Frontend | Next.js, Recharts, Tailwind CSS |
| CI/CD | GitHub Actions |

---

## Project Structure

```
mosaic/
├── CLAUDE.md                          # This file
├── README.md
├── .env.example                       # Environment variable template
├── .gitignore
│
├── infrastructure/                    # AWS CDK stack (TypeScript)
│   ├── bin/
│   │   └── mosaic.ts
│   ├── lib/
│   │   └── mosaic-stack.ts        # All AWS resources defined here
│   ├── package.json
│   └── cdk.json
│
├── backend/                           # Python ML + API layer
│   ├── requirements.txt
│   ├── plaid/
│   │   ├── __init__.py
│   │   ├── client.py                  # Plaid SDK client initialization
│   │   ├── sync.py                    # Pull + normalize transaction data
│   │   └── models.py                  # Pydantic models for Plaid data
│   ├── features/
│   │   ├── __init__.py
│   │   ├── engineer.py                # Feature engineering pipeline
│   │   ├── normalize.py               # Merchant name normalization
│   │   └── constants.py               # Spending category mappings
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── cluster.py                 # K-Means + DBSCAN clustering
│   │   ├── evaluate.py                # Silhouette score, elbow method
│   │   ├── pca.py                     # Dimensionality reduction for viz
│   │   └── train.py                   # Model training entrypoint
│   ├── bedrock/
│   │   ├── __init__.py
│   │   ├── client.py                  # Bedrock client initialization
│   │   └── persona.py                 # Persona description generation
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app (local dev)
│   │   └── routes/
│   │       ├── plaid.py               # Plaid sync endpoints
│   │       ├── classify.py            # User classification endpoints
│   │       └── personas.py            # Persona retrieval endpoints
│   └── lambdas/                       # Lambda handler wrappers
│       ├── plaid_sync.py              # Trigger Plaid data pull
│       ├── classify_user.py           # Feature engineer + assign cluster
│       ├── generate_persona.py        # Call Bedrock for persona description
│       └── get_persona.py             # Serve persona to frontend
│
├── frontend/                          # Next.js dashboard
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx               # Main dashboard page
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── PersonaCard.tsx        # Persona name + description card
│   │   │   ├── SpendingBreakdown.tsx  # Donut chart by category
│   │   │   ├── PersonaScatter.tsx     # PCA scatter plot of all personas
│   │   │   ├── PeerComparison.tsx     # vs. cluster average bar chart
│   │   │   ├── BedrockInsights.tsx    # 3 tailored recommendations
│   │   │   └── UserSwitcher.tsx       # Toggle between sandbox test users
│   │   ├── lib/
│   │   │   ├── api.ts                 # API client calling Lambda endpoints
│   │   │   └── types.ts               # TypeScript types
│   │   └── hooks/
│   │       └── usePersona.ts          # Data fetching hook
│   └── public/
│
└── scripts/
    ├── seed_dynamo.py                 # Seed DynamoDB with initial data
    ├── train_model.py                 # Run model training + upload to S3
    └── test_plaid.py                  # Verify Plaid Sandbox connection
```

---

## Environment Variables

Create a `.env` file at the project root based on `.env.example`:

```bash
# Plaid
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_sandbox_secret
PLAID_ENV=sandbox

# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# DynamoDB Table Names (set by CDK outputs)
DYNAMO_USERS_TABLE=mosaic-users
DYNAMO_PERSONAS_TABLE=mosaic-personas
DYNAMO_TRANSACTIONS_TABLE=mosaic-transactions

# S3
S3_MODEL_BUCKET=mosaic-models

# Bedrock
BEDROCK_MODEL_ID=claude-sonnet-4-6
BEDROCK_REGION=us-east-1

# API
API_BASE_URL=https://your-api-gateway-url.amazonaws.com/prod
```

---

## DynamoDB Schema

### `mosaic-users`
```json
{
  "userId": "string (PK)",
  "plaidAccessToken": "string",
  "clusterId": "number",
  "personaId": "string",
  "featureVector": "map",
  "lastSynced": "string (ISO timestamp)",
  "pcaCoordinates": { "x": "number", "y": "number" }
}
```

### `mosaic-personas`
```json
{
  "personaId": "string (PK)",
  "clusterId": "number",
  "name": "string",
  "description": "string",
  "strengths": ["string"],
  "weaknesses": ["string"],
  "recommendations": ["string"],
  "centroidFeatures": "map",
  "memberCount": "number"
}
```

### `mosaic-transactions`
```json
{
  "userId": "string (PK)",
  "transactionId": "string (SK)",
  "amount": "number",
  "merchantName": "string",
  "normalizedMerchant": "string",
  "category": "string",
  "date": "string",
  "isRecurring": "boolean"
}
```

---

## Feature Engineering Pipeline

The feature engineering pipeline in `backend/features/engineer.py` computes the
following features per user from raw Plaid transactions. These are the inputs to
the clustering model.

### Spending Distribution (% of total spend)
- `pct_food_dining` — restaurants, cafes, food delivery
- `pct_shopping` — retail, online shopping, clothing
- `pct_entertainment` — streaming, events, hobbies
- `pct_travel` — flights, hotels, rideshare
- `pct_health_fitness` — gym, pharmacy, medical
- `pct_subscriptions` — recurring software/media charges
- `pct_groceries` — supermarkets, grocery delivery

### Behavioral Features
- `avg_transaction_size` — mean transaction amount
- `spending_volatility` — std deviation of monthly totals
- `weekend_spend_ratio` — % of spend on Sat/Sun
- `late_night_ratio` — % of transactions between 11pm-3am
- `unique_merchant_count` — number of distinct merchants per month
- `recurring_ratio` — recurring vs. one-time purchase ratio
- `savings_rate` — (income - spending) / income

### Temporal Features
- `month_end_spike` — ratio of last 5 days spend vs. month average
- `paycheck_to_paycheck` — bool, balance < 10% of monthly spend before payday
- `spending_trend` — linear regression slope of monthly totals (positive = increasing)

### Merchant Normalization (in `backend/features/normalize.py`)
Raw Plaid merchant names are noisy. Normalize before feature engineering:
- Strip store numbers: "WHOLEFDS #1234" → "Whole Foods"
- Handle abbreviations: "MCK" → "McDonald's"
- Use fuzzy matching (rapidfuzz) for near-duplicates
- Map to canonical merchant name + Plaid category

---

## ML Pipeline

### Model Training (`backend/ml/train.py`)
1. Load feature matrix from DynamoDB
2. Normalize with `StandardScaler`
3. Run elbow method (K=2 to 10) to find optimal K
4. Evaluate with silhouette score — target > 0.35
5. Train final K-Means model with optimal K
6. Also train DBSCAN for comparison
7. Run PCA (2 components) for visualization coordinates
8. Serialize model with joblib, upload to S3
9. Store cluster centroids + PCA coordinates in DynamoDB

### Expected Personas (approximate, will vary with real data)
| Persona | Key Signals |
|---|---|
| The Conscious Saver | High savings rate, low volatility, few merchants |
| The Foodie | High food/dining %, high merchant diversity |
| The Subscriber | High recurring ratio, stable monthly spend |
| The Impulsive Spender | High volatility, late night ratio, large transactions |
| The Traveler | Periodic spend spikes, high travel %, low day-to-day |

### Model Evaluation
- Primary: Silhouette score (target > 0.35)
- Secondary: Davies-Bouldin index (lower is better)
- Visual: PCA scatter plot — clusters should be visually separable

---

## Bedrock Persona Generation

File: `backend/bedrock/persona.py`

For each cluster centroid, call Bedrock with a structured prompt:

```python
PERSONA_PROMPT = """
You are a financial advisor analyzing a spending persona cluster.

Cluster characteristics (normalized feature values):
{feature_summary}

Top spending categories: {top_categories}
Behavioral signals: {behavioral_summary}

Generate a financial persona with the following JSON structure:
{{
  "name": "Creative 2-3 word persona name (e.g. 'The Conscious Saver')",
  "description": "2-3 sentence personality description of this spender type",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "recommendations": [
    "Specific actionable recommendation 1",
    "Specific actionable recommendation 2", 
    "Specific actionable recommendation 3"
  ]
}}

Return ONLY valid JSON. No preamble or explanation.
"""
```

Parse the JSON response and store in `mosaic-personas` DynamoDB table.
Regenerate persona descriptions only when cluster centroids change significantly
(cosine similarity < 0.95 vs. previous centroid).

---

## AWS Lambda Functions

### `plaid-sync`
- Trigger: API Gateway POST `/sync/{userId}`
- Action: Pull latest transactions from Plaid, normalize, store in DynamoDB
- Runtime: Python 3.12
- Timeout: 30s
- Memory: 256MB

### `classify-user`
- Trigger: API Gateway POST `/classify/{userId}`
- Action: Load user transactions, run feature engineering, assign cluster, store result
- Runtime: Python 3.12
- Timeout: 60s
- Memory: 512MB (loads ML model from S3)

### `generate-persona`
- Trigger: API Gateway POST `/persona/generate/{clusterId}`
- Action: Call Bedrock with cluster centroid, store generated persona in DynamoDB
- Runtime: Python 3.12
- Timeout: 30s
- Memory: 256MB

### `get-persona`
- Trigger: API Gateway GET `/persona/{userId}`
- Action: Return user's assigned persona + spending breakdown + PCA coordinates
- Runtime: Python 3.12
- Timeout: 10s
- Memory: 128MB

---

## CDK Stack

File: `infrastructure/lib/mosaic-stack.ts`

Resources to provision:
- 3x DynamoDB tables (users, personas, transactions) — PAY_PER_REQUEST billing
- 1x S3 bucket (model artifacts) — versioned, private
- 4x Lambda functions with appropriate IAM roles
- 1x API Gateway REST API with CORS enabled
- IAM roles scoped to least privilege:
  - Lambda → DynamoDB (read/write specific tables only)
  - Lambda → S3 (read model bucket only)
  - Lambda → Bedrock (InvokeModel on claude-sonnet-4-6 only)
- CloudWatch log groups for each Lambda

Output: API Gateway URL → used as `API_BASE_URL` in frontend `.env`

---

## Frontend Dashboard Components

### PersonaCard
Shows: persona name, description, strengths, weaknesses
Style: Large card with persona-specific color theme

### SpendingBreakdown
Shows: Donut chart of spending by category (Recharts PieChart)
Data: `featureVector` spending percentages from DynamoDB

### PersonaScatter
Shows: 2D scatter plot of all users in PCA space, current user highlighted
Data: `pcaCoordinates` for all users, colored by `clusterId`
Library: Recharts ScatterChart

### PeerComparison
Shows: Bar chart comparing user's feature values vs. cluster centroid average
Highlights where user is above/below their persona average

### BedrockInsights
Shows: 3 tailored recommendations from Bedrock persona generation
Style: Card list with icons

### UserSwitcher
Shows: Dropdown to switch between Plaid Sandbox test users
Purpose: Demo multiple personas without real user auth

---

## Development Phases

### Phase 1 — Plaid Integration
- [ ] Set up Plaid Sandbox account, get credentials
- [ ] Implement `backend/plaid/client.py` — initialize Plaid client
- [ ] Implement `backend/plaid/sync.py` — pull + store transactions
- [ ] Implement `backend/features/normalize.py` — merchant normalization
- [ ] Test with `scripts/test_plaid.py` — verify data pulling correctly
- [ ] Store raw transactions in DynamoDB

### Phase 2 — Feature Engineering + ML
- [ ] Implement `backend/features/engineer.py` — all 15+ features
- [ ] Run elbow method to determine optimal K
- [ ] Train K-Means model, evaluate silhouette score
- [ ] Train DBSCAN model, compare results
- [ ] Run PCA, store 2D coordinates per user
- [ ] Serialize model, upload to S3 via `scripts/train_model.py`

### Phase 3 — Bedrock Persona Generation
- [ ] Implement `backend/bedrock/client.py`
- [ ] Implement `backend/bedrock/persona.py` with prompt template
- [ ] Generate personas for each cluster centroid
- [ ] Store in `mosaic-personas` DynamoDB table
- [ ] Validate JSON output parsing

### Phase 4 — AWS Deployment
- [ ] Write CDK stack in `infrastructure/lib/mosaic-stack.ts`
- [ ] Deploy DynamoDB tables + S3 bucket
- [ ] Package + deploy 4 Lambda functions
- [ ] Configure API Gateway routes
- [ ] Set up IAM roles with least privilege
- [ ] Set up GitHub Actions CI/CD pipeline
- [ ] Test all endpoints end-to-end

### Phase 5 — Frontend Dashboard
- [ ] Set up Next.js project with Tailwind
- [ ] Implement API client in `lib/api.ts`
- [ ] Build PersonaCard component
- [ ] Build SpendingBreakdown donut chart
- [ ] Build PersonaScatter plot
- [ ] Build PeerComparison bar chart
- [ ] Build BedrockInsights component
- [ ] Build UserSwitcher dropdown
- [ ] Polish UI, ensure mobile responsive

### Phase 6 — Polish + Documentation
- [ ] Write comprehensive README with architecture diagram
- [ ] Add demo GIF/video to README
- [ ] Clean up code, add docstrings
- [ ] Ensure all env vars documented in `.env.example`
- [ ] Deploy frontend to Vercel or Amplify
- [ ] Final end-to-end test with all Plaid sandbox users

---

## Plaid Sandbox Test Users

Plaid provides preset sandbox credentials for testing. Each simulates a different
financial profile — use all of them to generate diverse personas:

| Username | Password | Profile |
|---|---|---|
| `user_good` | `pass_good` | Good standing, regular income |
| `user_custom` | `pass_good` | Customizable transactions |
| `user_employee` | `pass_good` | Salaried employee profile |

Use `UserSwitcher` in the frontend to toggle between these for demo purposes.

---

## Common Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload          # Local FastAPI dev server

# Test Plaid connection
python scripts/test_plaid.py

# Train ML model
python scripts/train_model.py

# Infrastructure
cd infrastructure
npm install
cdk bootstrap                          # First time only
cdk deploy                             # Deploy all resources
cdk destroy                            # Tear down all resources

# Frontend
cd frontend
npm install
npm run dev                            # Local Next.js dev server
npm run build                          # Production build
```

---

## Key Design Decisions

**Why K-Means + DBSCAN?**
K-Means is interpretable and interview-friendly. DBSCAN handles outliers and doesn't
require specifying K upfront. Running both and comparing shows deeper ML understanding.

**Why unsupervised over supervised?**
No labeled "persona" data exists. Unsupervised clustering discovers natural groupings
in the data rather than imposing predetermined categories. More honest and more
sophisticated than a classifier.

**Why Bedrock for persona generation vs. hardcoding labels?**
Hardcoded labels are brittle — if cluster characteristics shift with new data, labels
become inaccurate. Bedrock generates descriptions dynamically from cluster centroids,
making the system adaptive. Also showcases AI integration naturally.

**Why FastAPI locally + Lambda in production?**
FastAPI allows rapid local development and testing. Lambda wrappers in
`backend/lambdas/` are thin handlers that call the same underlying business logic.
No code duplication — same feature engineering and ML code runs in both environments.

**Why CDK over SAM or Terraform?**
CDK is what Isaac used at Principal Financial Group. Consistency in tooling across
internship and personal projects demonstrates depth of knowledge, not just exposure.

---

## Talking Points

1. **Merchant normalization** — "Raw Plaid data has noisy merchant names. I used fuzzy
   matching to normalize 'WHOLEFDS #1234' and 'WHOLE FOODS MARKET' to the same entity
   before feature engineering."

2. **Choosing K** — "I used the elbow method and silhouette scoring to determine the
   optimal number of clusters rather than just guessing. The silhouette score told me
   K=5 gave the most distinct, well-separated personas."

3. **DBSCAN vs K-Means** — "K-Means assumes spherical clusters of equal size. I also
   ran DBSCAN which is density-based and handles outliers as noise rather than forcing
   them into a cluster. Comparing both gave me confidence in the results."

4. **Why Bedrock** — "Rather than hardcoding persona labels that might become inaccurate
   as the model retrains, I generate descriptions dynamically from cluster centroids using
   Bedrock. The system stays accurate even as spending patterns shift."

5. **CDK** — "I used the same IaC approach I used at Principal — provisioning all
   resources as code means the entire infrastructure is reproducible and version controlled."
