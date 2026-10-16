
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.billing import Plan, Subscription, UsageEvent
from app.services.pricing import (
    PRICING_VERSION,
    calculate_api_call_cost,
    calculate_token_cost,
)


class MeteringError(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def record_usage(
    db: Session,
    tenant_id: str,
    usage_type: str,
    quantity: int,
    idempotency_key: str,
) -> dict:
    """Record usage once, enforce quotas, and calculate its cost."""

    if usage_type not in {"api_call", "ai_tokens"}:
        raise MeteringError(
            "Invalid usage type. Use api_call or ai_tokens.",
            422,
        )

    if quantity <= 0:
        raise MeteringError(
            "Quantity must be greater than zero.",
            422,
        )

    if not idempotency_key or len(idempotency_key) > 255:
        raise MeteringError(
            "A valid idempotency key is required.",
            422,
        )

    # Check whether this request has already been recorded.
    existing = db.scalar(
        select(UsageEvent).where(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.idempotency_key == idempotency_key,
        )
    )

    if existing is not None:
        if (
            existing.usage_type != usage_type
            or existing.quantity != quantity
        ):
            raise MeteringError(
                "This idempotency key was already used for a different request.",
                409,
            )

        return {
            "id": existing.id,
            "tenant_id": existing.tenant_id,
            "usage_type": existing.usage_type,
            "quantity": existing.quantity,
            "idempotency_key": existing.idempotency_key,
            "cost_micro_usd": existing.cost_micro_usd,
            "pricing_version": existing.pricing_version,
            "duplicate": True,
        }

    # Confirm the tenant has an active subscription.
    subscription = db.scalar(
        select(Subscription).where(
            Subscription.tenant_id == tenant_id,
            Subscription.status == "active",
        )
    )

    if subscription is None:
        raise MeteringError(
            "No active subscription was found for this tenant.",
            402,
        )

    # Find the plan attached to the active subscription.
    plan = db.get(Plan, subscription.plan_id)

    if plan is None:
        raise MeteringError(
            "The subscription plan could not be found.",
            500,
        )

    # Calculate usage for the current calendar month.
    now = datetime.now(timezone.utc)
    month_start = datetime(
        now.year,
        now.month,
        1,
        tzinfo=timezone.utc,
    )

    monthly_usage = db.scalar(
        select(UsageEvent.usage_type, UsageEvent.quantity)
        .where(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.created_at >= month_start,
        )
    )

    # Sum usage by type so each plan limit is checked independently.
    usage_rows = db.execute(
        select(
            UsageEvent.usage_type,
            UsageEvent.quantity,
        ).where(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.created_at >= month_start,
        )
    ).all()

    api_calls_used = sum(
        row.quantity
        for row in usage_rows
        if row.usage_type == "api_call"
    )

    tokens_used = sum(
        row.quantity
        for row in usage_rows
        if row.usage_type == "ai_tokens"
    )

    if usage_type == "api_call":
        if api_calls_used + quantity > plan.api_call_limit:
            raise MeteringError(
                "API call quota exceeded for the current month.",
                429,
            )

        cost_micro_usd = calculate_api_call_cost(quantity)

    else:
        if tokens_used + quantity > plan.token_limit:
            raise MeteringError(
                "AI token quota exceeded for the current month.",
                429,
            )

        # For aggregate token metering, quantity is treated as
        # regular input tokens until detailed token breakdown is available.
        cost_micro_usd = calculate_token_cost(
            input_tokens=quantity,
        )

    # Save the event with its cost and pricing version.
    event = UsageEvent(
        tenant_id=tenant_id,
        usage_type=usage_type,
        quantity=quantity,
        cost_micro_usd=cost_micro_usd,
        pricing_version=PRICING_VERSION,
        idempotency_key=idempotency_key,
    )

    try:
        db.add(event)
        db.commit()
        db.refresh(event)

    except IntegrityError:
        db.rollback()

        # Another request may have recorded this key at the same time.
        existing = db.scalar(
            select(UsageEvent).where(
                UsageEvent.tenant_id == tenant_id,
                UsageEvent.idempotency_key == idempotency_key,
            )
        )

        if existing is None:
            raise MeteringError(
                "Usage could not be recorded. Please retry with the same key.",
                503,
            )

        if (
            existing.usage_type != usage_type
            or existing.quantity != quantity
        ):
            raise MeteringError(
                "This idempotency key was already used for a different request.",
                409,
            )

        return {
            "id": existing.id,
            "tenant_id": existing.tenant_id,
            "usage_type": existing.usage_type,
            "quantity": existing.quantity,
            "idempotency_key": existing.idempotency_key,
            "cost_micro_usd": existing.cost_micro_usd,
            "pricing_version": existing.pricing_version,
            "duplicate": True,
        }

    return {
        "id": event.id,
        "tenant_id": event.tenant_id,
        "usage_type": event.usage_type,
        "quantity": event.quantity,
        "idempotency_key": event.idempotency_key,
        "cost_micro_usd": event.cost_micro_usd,
        "pricing_version": event.pricing_version,
        "duplicate": False,
    }
