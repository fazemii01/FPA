from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class WilayahCreate(BaseModel):
    name: str
    credits: int = 0

    @field_validator("credits")
    @classmethod
    def validate_credits(cls, v):
        if v < 0:
            raise ValueError("Kredit wilayah tidak boleh negatif")
        return v


class WilayahResponse(BaseModel):
    id: int
    name: str
    credits: int
    created_at: datetime
    updated_at: datetime
    lembaga_count: int = 0
    super_admin_email: Optional[str] = None
    super_admin_name: Optional[str] = None

    class Config:
        from_attributes = True


class WilayahTopUp(BaseModel):
    credits: int

    @field_validator("credits")
    @classmethod
    def validate_credits(cls, v):
        if v <= 0:
            raise ValueError("Kredit topup harus bernilai positif")
        return v
