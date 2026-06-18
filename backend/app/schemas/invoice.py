from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class InvoiceCreate(BaseModel):
    lembaga_id: int
    client_name: str
    description: str
    credits: int
    discount: float = 0.0

    @field_validator("credits")
    @classmethod
    def validate_credits(cls, v):
        if v <= 0:
            raise ValueError("Kredit harus bernilai positif")
        return v


class InvoiceResponse(BaseModel):
    id: int
    uuid: str
    code: str
    lembaga_id: int
    lembaga_name: Optional[str] = None
    client_name: str
    description: str
    credits: int
    discount: float
    total_amount: float
    status: str
    payment_proof_path: Optional[str] = None
    payment_proof_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
