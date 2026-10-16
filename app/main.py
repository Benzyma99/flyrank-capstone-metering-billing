from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import GenerateRequest
from app.services.metering import MeteringError, record_usage

app = FastAPI(
    title="Usage Metering & Billing Engine",
    description="Usage tracking, quotas, and subscription billing.",
    version="0.2.0",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "usage-metering-billing-engine",
    }


@app.post("/generate", tags=["Metering"])
def generate(
    request: GenerateRequest,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=1,
        max_length=255,
    ),
    db: Session = Depends(get_db),
):
    try:
        return record_usage(
            db=db,
            tenant_id=request.tenant_id,
            usage_type=request.usage_type,
            quantity=request.quantity,
            idempotency_key=idempotency_key,
        )
    except MeteringError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from exc
@app.get("/usage", tags=["Metering"])
def get_usage(
    tenant_id: str = "demo-tenant",
    db: Session = Depends(get_db),
):
    return {
        "message": "Usage endpoint registered",
        "tenant_id": tenant_id,
    }
