
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True
    )
    api_call_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    token_limit: Mapped[int] = mapped_column(Integer, nullable=False)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), nullable=False, unique=True
    )
    plan_id: Mapped[str] = mapped_column(
        ForeignKey("plans.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="active"
    )


class UsageEvent(Base):
    __tablename__ = "usage_events"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_usage_tenant_idempotency",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), nullable=False, index=True
    )
    usage_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Cost is stored as an integer number of micro-USD.
    cost_micro_usd: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )
    pricing_version: Mapped[str] = mapped_column(
        String(32), nullable=False, default="legacy"
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        index=True,
    )
