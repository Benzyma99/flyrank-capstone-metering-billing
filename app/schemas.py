
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    tenant_id: str = Field(default="demo-tenant", min_length=1, max_length=64)
    usage_type: str = Field(pattern="^(api_call|ai_tokens)$")
    quantity: int = Field(gt=0)
