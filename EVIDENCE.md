
# Evidence — Usage Metering & Billing Engine

## 1. Automated Tests

**Last confirmed result:** 11 passed, 1 warning.

Command used:

```powershell
python -m pytest -q
```

The tests cover pricing calculations and core metering behavior, including idempotency, quota enforcement, and inactive subscriptions.

This result reflects the last confirmed test run; rerun the tests to verify the current project state.

## 2. Database Migration

The pricing-fields migration was applied successfully.

Migration revision:

`e1c39e5fc31d`

Migration description:

`add usage event pricing fields`

The migration adds:

- `cost_micro_usd`
- `pricing_version`

The migration status was verified using:

```powershell
python -m alembic current
```

The reported revision was:

`e1c39e5fc31d (head)`

## 3. Source Code Repository

GitHub repository:

https://github.com/Benzyma99/flyrank-capstone-metering-billing

The application foundation was committed and pushed to this repository.

## 4. Features Covered by the Tests

The confirmed test suite includes checks for:

- Health endpoint response.
- Required idempotency key.
- Duplicate usage requests being recorded once.
- Conflicting requests using the same idempotency key.
- API-call quota enforcement.
- Inactive subscription handling.
- Pricing calculations.

## 5. Evidence Still to Collect

The following evidence should be added when available:

- A fresh test-run result after documentation is completed.
- Screenshots or captured responses from the API documentation page.
- Example successful usage-recording response.
- Example duplicate-request response.
- Example quota-exceeded response.
- Evidence of Stripe test-mode checkout and webhook handling after implementation.
- Evidence of the background job, retry behavior, and failure alerts after implementation.

## 6. Accuracy Statement

This document records evidence that has been confirmed during development. Features listed as future evidence requirements must not be treated as implemented or verified.
