from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class FingerPositionEnum(str, Enum):
    LEFT_THUMB = "left_thumb"
    LEFT_INDEX = "left_index"
    LEFT_MIDDLE = "left_middle"
    LEFT_RING = "left_ring"
    LEFT_PINKY = "left_pinky"
    RIGHT_THUMB = "right_thumb"
    RIGHT_INDEX = "right_index"
    RIGHT_MIDDLE = "right_middle"
    RIGHT_RING = "right_ring"
    RIGHT_PINKY = "right_pinky"


class FingerprintCreate(BaseModel):
    finger_position: FingerPositionEnum


class FingerprintResponse(BaseModel):
    id: int
    scan_session_id: int
    finger_position: FingerPositionEnum
    image_path: str
    quality_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class SessionStatusEnum(str, Enum):
    DRAFT = "draft"
    REGISTERED = "registered"
    SCANNING = "scanning"
    SCAN_COMPLETED = "scan_completed"
    WAITING_FOR_REVIEW = "waiting_for_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEED_RESCAN = "need_rescan"
    GENERATING_REPORT = "generating_report"
    REPORT_GENERATED = "report_generated"


class ScanSessionCreate(BaseModel):
    participant_name: str = Field(..., min_length=1, max_length=120)
    participant_age: int = Field(..., ge=0, le=150)
    participant_gender: Optional[str] = Field(default=None, max_length=16)
    notes: Optional[str] = None


class ScanSessionResponse(BaseModel):
    id: int
    user_id: int
    participant_name: str
    participant_age: int
    participant_gender: Optional[str]
    notes: Optional[str]
    status: SessionStatusEnum
    submitted_at: Optional[datetime]
    reviewed_by_id: Optional[int]
    reviewed_at: Optional[datetime]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    fingerprints: List[FingerprintResponse] = []

    class Config:
        from_attributes = True


class SessionRejectRequest(BaseModel):
    reason: str = Field(..., min_length=1)


class SessionRescanRequest(BaseModel):
    finger_positions: List[FingerPositionEnum] = Field(default_factory=list)
    reason: Optional[str] = None


class ReportMetrics(BaseModel):
    total_fingerprints: int
    quality_scores: Dict[str, float]
    average_quality: float


class ReportResponse(BaseModel):
    id: int
    scan_session_id: int
    overall_score: float
    pdf_path: Optional[str]
    metrics: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
