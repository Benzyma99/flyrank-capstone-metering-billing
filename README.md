
# Usage Metering & Billing Engine

A Python-based API service that records tenant usage, enforces subscription quotas, and calculates usage costs. This project is being developed as part of the FlyRank Backend Track capstone.

## Current Features

- FastAPI application with a health endpoint.
- Tenant, plan, subscription, and usage-event database models.
- Usage recording for API calls and AI tokens.
- Idempotency keys to prevent duplicate usage records.
- Conflict detection when an idempotency key is reused with different request data.
- Monthly quota enforcement.
- HTTP 429 responses when usage exceeds a plan limit.
- HTTP 402 responses when a tenant has no active subscription.
- Cost calculation using integer micro-USD values.
- Pricing version stored with each usage event.
- Database migrations using Alembic.
- Automated tests using pytest.

## Technology Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite for local development
- Alembic
- pytest
- HTTPX

## Project Structure

```text
.
├── alembic/
├── alembic.ini
├── app/
│   ├── models/
│   └── services/
├── tests/
├── .gitignore
├── README.md
├── DESIGN.md
├── BUILDLOG.md
├── EVIDENCE.md
└── capstone.yaml
```

## Local Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Benzyma99/flyrank-capstone-metering-billing.git
   cd flyrank-capstone-metering-billing
   ```

2. Create and activate a virtual environment.

   Windows PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Apply database migrations:

   ```powershell
   python -m alembic upgrade head
   ```

5. Run the development server:

   ```powershell
   uvicorn app.main:app --reload
   ```

6. Open the interactive API documentation:

   http://127.0.0.1:8000/docs

## Running Tests

Run:

```powershell
python -m pytest -q
```

The last confirmed test run reported 11 passing tests.

## Pricing Notes

The current pricing rates are demonstration rates for this capstone, not verified prices from an AI provider. Costs are stored in integer micro-USD, where one US dollar equals 1,000,000 micro-USD.

For aggregate AI-token usage, the current implementation treats the submitted quantity as regular input tokens. Detailed input, cached-input, and output-token breakdowns require further integration.

## Development Status

The metering and pricing foundation has been implemented and pushed to GitHub. The full billing system is still under development.

Features such as production-ready Stripe checkout and webhook handling, background jobs with retries and failure alerts, and complete deployment documentation must not be considered complete until they are implemented and tested.

## Repository

https://github.com/Benzyma99/flyrank-capstone-metering-billing
