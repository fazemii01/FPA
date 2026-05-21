from pydantic import BaseModel
from typing import Optional, List
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
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanSessionCreate(BaseModel):
    pass


class ScanSessionResponse(BaseModel):
    id: int
    user_id: int
    status: SessionStatusEnum
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    fingerprints: List[FingerprintResponse] = []
    
    class Config:
        from_attributes = True


class ReportMetrics(BaseModel):
    total_fingerprints: int
    quality_scores: dict
    average_quality: float


class ReportResponse(BaseModel):
    id: int
    scan_session_id: int
    overall_score: float
    pdf_path: Optional[str]
    metrics: Optional[ReportMetrics]
    created_at: datetime
    
    class Config:
        from_attributes = True
