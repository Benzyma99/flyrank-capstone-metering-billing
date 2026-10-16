
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.billing import Plan, Subscription, Tenant, UsageEvent

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with TestingSessionLocal() as db:
        db.add_all([
            Plan(
                id="free",
                name="Free",
                api_call_limit=2,
                token_limit=100,
            ),
            Plan(
                id="pro",
                name="Pro",
                api_call_limit=10,
                token_limit=1000,
            ),
            Tenant(id="test-tenant", name="Test Tenant"),
        ])
        db.flush()
        db.add(
            Subscription(
                tenant_id="test-tenant",
                plan_id="free",
                status="active",
            )
        )
        db.commit()


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_requires_idempotency_key():
    setup_database()
    response = client.post(
        "/generate",
        json={
            "tenant_id": "test-tenant",
            "usage_type": "api_call",
            "quantity": 1,
        },
    )
    assert response.status_code == 422


def test_same_request_is_recorded_once():
    setup_database()
    payload = {
        "tenant_id": "test-tenant",
        "usage_type": "api_call",
        "quantity": 1,
    }
    headers = {"Idempotency-Key": "retry-001"}

    first = client.post("/generate", json=payload, headers=headers)
    second = client.post("/generate", json=payload, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200

    first_data = first.json()
    second_data = second.json()

    assert first_data["id"] == second_data["id"]
    assert first_data["duplicate"] is False
    assert second_data["duplicate"] is True

    # Both responses must return the same saved cost and pricing version.
    assert "cost_micro_usd" in first_data
    assert "pricing_version" in first_data
    assert first_data["cost_micro_usd"] == second_data["cost_micro_usd"]
    assert first_data["pricing_version"] == second_data["pricing_version"]

    with TestingSessionLocal() as db:
        events = db.scalars(
            select(UsageEvent).where(
                UsageEvent.tenant_id == "test-tenant"
            )
        ).all()

        assert len(events) == 1
        assert events[0].cost_micro_usd == first_data["cost_micro_usd"]
        assert events[0].pricing_version == first_data["pricing_version"]

    with TestingSessionLocal() as db:
        events = db.scalars(
            select(UsageEvent).where(
                UsageEvent.tenant_id == "test-tenant"
            )
        ).all()
        assert len(events) == 1


def test_reusing_key_with_different_quantity_returns_conflict():
    setup_database()
    headers = {"Idempotency-Key": "retry-002"}

    first = client.post(
        "/generate",
        json={
            "tenant_id": "test-tenant",
            "usage_type": "api_call",
            "quantity": 1,
        },
        headers=headers,
    )
    second = client.post(
        "/generate",
        json={
            "tenant_id": "test-tenant",
            "usage_type": "api_call",
            "quantity": 2,
        },
        headers=headers,
    )

    assert first.status_code == 200
    assert second.status_code == 409


def test_quota_exceeded_returns_429():
    setup_database()

    for key in ("quota-001", "quota-002"):
        response = client.post(
            "/generate",
            json={
                "tenant_id": "test-tenant",
                "usage_type": "api_call",
                "quantity": 1,
            },
            headers={"Idempotency-Key": key},
        )
        assert response.status_code == 200

    response = client.post(
        "/generate",
        json={
            "tenant_id": "test-tenant",
            "usage_type": "api_call",
            "quantity": 1,
        },
        headers={"Idempotency-Key": "quota-003"},
    )

    assert response.status_code == 429

def test_inactive_subscription_returns_402():
    setup_database()

    with TestingSessionLocal() as db:
        subscription = db.scalar(
            select(Subscription).where(
                Subscription.tenant_id == "test-tenant"
            )
        )
        subscription.status = "cancelled"
        db.commit()

    response = client.post(
        "/generate",
        headers={"Idempotency-Key": "payment-required-001"},
        json={
            "tenant_id": "test-tenant",
            "usage_type": "api_call",
            "quantity": 1,
        },
    )

    assert response.status_code == 402
