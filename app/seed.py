
from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models.billing import Plan, Tenant, Subscription


def seed_database():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        plans = [
            {
                "id": "free",
                "name": "Free",
                "api_call_limit": 1000,
                "token_limit": 100_000,
            },
            {
                "id": "pro",
                "name": "Pro",
                "api_call_limit": 10_000,
                "token_limit": 1_000_000,
            },
        ]

        for plan_data in plans:
            existing = db.get(Plan, plan_data["id"])
            if existing is None:
                db.add(Plan(**plan_data))

        existing_tenant = db.get(Tenant, "demo-tenant")
        if existing_tenant is None:
            db.add(
                Tenant(
                    id="demo-tenant",
                    name="Demo Tenant",
                )
            )

        db.flush()

        existing_subscription = db.scalar(
            select(Subscription).where(
                Subscription.tenant_id == "demo-tenant"
            )
        )

        if existing_subscription is None:
            db.add(
                Subscription(
                    tenant_id="demo-tenant",
                    plan_id="free",
                    status="active",
                )
            )

        db.commit()

    print("Database initialized. Free and Pro plans are ready.")


if __name__ == "__main__":
    seed_database()
