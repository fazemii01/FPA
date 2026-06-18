from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.database import Base


class SessionStatus(str, Enum):
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


class ScanSession(Base):
    __tablename__ = "scan_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lembaga_id = Column(Integer, ForeignKey("lembaga.id"), nullable=True)

    # Participant data (participants are not users)
    participant_name = Column(String(120), nullable=False, default="")
    participant_age = Column(Integer, nullable=False, default=0)
    participant_gender = Column(String(16), nullable=True)
    notes = Column(Text, nullable=True)

    # Lifecycle
    status = Column(SQLEnum(SessionStatus, name="sessionstatus", values_callable=lambda x: [e.value for e in x]), default=SessionStatus.DRAFT)
    submitted_at = Column(DateTime, nullable=True)
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="scan_sessions", foreign_keys=[user_id])
    lembaga = relationship("Lembaga", back_populates="scan_sessions")
    reviewed_by = relationship("User", back_populates="reviewed_sessions", foreign_keys=[reviewed_by_id])
    fingerprints = relationship("Fingerprint", back_populates="scan_session", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="scan_session", uselist=False)
