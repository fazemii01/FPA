from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class FingerprintFeature(Base):
    __tablename__ = "fingerprint_features"

    id = Column(Integer, primary_key=True, index=True)
    fingerprint_id = Column(Integer, ForeignKey("fingerprints.id"), nullable=False, unique=True)
    scan_session_id = Column(Integer, ForeignKey("scan_sessions.id"), nullable=False, index=True)
    pattern_type = Column(String(32), nullable=False)
    ridge_count = Column(Integer, nullable=False, default=0)
    ridge_density = Column(Float, nullable=False, default=0.0)
    orientation_stability = Column(Float, nullable=False, default=0.0)
    minutiae_count = Column(Integer, nullable=False, default=0)
    core_count = Column(Integer, nullable=False, default=0)
    delta_count = Column(Integer, nullable=False, default=0)
    quality_score = Column(Float, nullable=False, default=0.0)
    features_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    fingerprint = relationship("Fingerprint", back_populates="features")
    scan_session = relationship("ScanSession")
