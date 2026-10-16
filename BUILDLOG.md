
# Build Log — Usage Metering & Billing Engine

## Project Overview

This log records development progress for the FlyRank Backend Track capstone. Entries describe completed work and the current state of the implementation.

## Completed Work

### 1. Project Setup

- Created a dedicated project repository.
- Set up the Python application structure.
- Added dependencies for FastAPI, SQLAlchemy, Alembic, pricing, and testing.
- Configured Git ignore rules for local environment and database files.

### 2. Database Foundation

- Created database models for tenants, plans, subscriptions, and usage events.
- Configured SQLite for local development.
- Set up Alembic for database migrations.
- Added pricing fields to usage events:
  - `cost_micro_usd`
  - `pricing_version`
- Successfully applied the migration that adds these fields.

### 3. Usage Metering

- Implemented usage recording for API calls and AI-token quantities.
- Added idempotency-key handling to avoid recording the same request twice.
- Added conflict handling for reuse of a key with different request data.
- Added checks for active subscriptions and plan limits.
- Added quota-exceeded responses.

### 4. Pricing Foundation

- Created a pricing service for API-call and aggregate token costs.
- Used integer micro-USD values to represent costs.
- Added a pricing version to recorded usage events.
- Added automated pricing tests.

### 5. Automated Testing

- Added tests for pricing calculations.
- Added tests for usage recording, duplicate requests, conflicting idempotency keys, quotas, and inactive subscriptions.
- The last confirmed test run reported 11 passing tests and 1 warning.

### 6. Version Control

- Updated `.gitignore` to exclude local environment files, virtual environments, database files, and Python cache files.
- Committed the application foundation and pushed it to the GitHub repository.

Repository:

https://github.com/Benzyma99/flyrank-capstone-metering-billing

## Current Status

The metering and pricing foundation is implemented, and the last confirmed test run passed.

## Remaining Work

The following work remains to be implemented or verified:

- Review and complete the project documentation.
- Verify tenant-specific usage reporting and quota behavior.
- Add detailed token breakdowns for regular input, cached input, and output tokens.
- Implement and test Stripe Checkout and secure webhook processing.
- Add a background job with retries and failure alerts.
- Expand integration and error-handling tests.
- Review deployment configuration and final capstone requirements.

## Development Principle

Features are marked complete only after implementation and appropriate testing. Planned work is not reported as completed work.
