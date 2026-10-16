
# System Design — Usage Metering & Billing Engine

## 1. Purpose

The Usage Metering & Billing Engine records usage for individual tenants, checks subscription limits, and calculates usage costs. It is being developed as part of the FlyRank Backend Track capstone.

## 2. Current Architecture

The current design uses a FastAPI application, SQLAlchemy for database access, and SQLite for local development.

```text
Client
  |
  v
FastAPI Application
  |
  v
Usage Metering Service
  |
  +--> Validate usage request
  |
  +--> Check idempotency key
  |
  +--> Check active subscription and plan
  |
  +--> Calculate monthly usage
  |
  +--> Enforce plan quota
  |
  +--> Calculate usage cost
  |
  v
SQLAlchemy
  |
  v
SQLite Database
```

## 3. Main Components

### FastAPI Application

The application exposes HTTP endpoints, including health checks, usage generation, and usage summaries.

### Database Models

The current data model includes:

- **Tenant:** represents a customer or organization using the service.
- **Plan:** stores plan limits, including API-call and token limits.
- **Subscription:** connects a tenant to a plan and tracks subscription status.
- **UsageEvent:** records a usage event, its quantity, idempotency key, calculated cost, pricing version, and creation time.

### Metering Service

The metering service validates requests, checks subscriptions, enforces monthly quotas, and records usage events.

### Pricing Service

The pricing service calculates costs using integer micro-USD values. A pricing version is saved with each usage event to identify the rate version used for the calculation.

### Database Migrations

Alembic manages database schema changes so the database can be updated in a controlled way.

## 4. Usage Recording Flow

1. A client submits a usage request.
2. The service validates the usage type, quantity, and idempotency key.
3. The service checks whether the same key has already been used by that tenant.
4. If the same request was already recorded, the existing event is returned without recording it again.
5. If the key was reused with different request data, the service returns a conflict response.
6. The service checks for an active subscription and loads the associated plan.
7. The service calculates monthly usage and checks the applicable quota.
8. If the quota is exceeded, the service rejects the request.
9. Otherwise, the service calculates the usage cost and saves the event.

## 5. Idempotency

Idempotency prevents retries from recording the same usage more than once. Each usage event has an idempotency key, and the database enforces uniqueness for the combination of tenant ID and key.

## 6. Quotas and HTTP Responses

The current implementation uses:

- **200:** successful usage recording or an accepted duplicate request.
- **402:** no active subscription.
- **409:** an idempotency key is reused with different request data.
- **422:** invalid request data.
- **429:** the plan's usage limit has been exceeded.

Other errors may occur for unexpected database or application failures.

## 7. Pricing

The current pricing service supports API-call pricing and aggregate token pricing.

Costs are stored as integer micro-USD:

- 1 USD = 1,000,000 micro-USD.
- API calls use a configured demonstration rate.
- Aggregate token usage is currently treated as regular input tokens.
- The pricing version is stored with each usage event.

Detailed cached-input and output-token pricing must be connected to a more detailed usage payload before it can be applied accurately to real provider usage.

## 8. Current Limitations

The current implementation is a development foundation, not a production-ready billing platform.

The following areas require further implementation or verification:

- Stripe Checkout and verified, deduplicated webhooks.
- Detailed AI token usage reporting.
- Background jobs with retries and failure alerts.
- Production database configuration and deployment.
- Authentication and authorization for tenant-specific requests.
- Broader integration and failure-recovery tests.

These items should only be marked complete after they are implemented and tested.

## 9. Technology Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite for local development
- Alembic
- pytest
- HTTPX
