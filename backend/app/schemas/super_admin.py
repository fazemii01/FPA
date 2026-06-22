from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class LembagaCreate(BaseModel):
    name: str
    credits: int = 0
    is_active: bool = True
    type: str = "umum"


class LembagaUpdate(BaseModel):
    name: Optional[str] = None
    credits: Optional[int] = None
    is_active: Optional[bool] = None
    type: Optional[str] = None


class LembagaResponse(BaseModel):
    id: int
    name: str
    credits: int
    is_active: bool
    type: str
    created_at: datetime
    users_count: int = 0
    reports_count: int = 0

    class Config:
        from_attributes = True


class TopUpRequest(BaseModel):
    amount: float
    credits: int
    reference_no: Optional[str] = None


class PermissionMappingUpdate(BaseModel):
    role: str
    permissions: List[str]


class PaymentLogResponse(BaseModel):
    id: int
    lembaga_id: int
    lembaga_name: str
    amount: float
    credits_added: int
    status: str
    reference_no: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserAuditResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    lembaga_id: Optional[int]
    lembaga_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStatsResponse(BaseModel):
    total_lembaga: int
    total_credits: int
    total_users: int
    total_scans: int
    total_reports: int
    recent_sessions: List[dict] = []
    credit_summary: List[dict] = []
