from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_session_id = Column(Integer, ForeignKey("scan_sessions.id"), nullable=False, unique=True)
    lembaga_id = Column(Integer, ForeignKey("lembaga.id"), nullable=True)
    overall_score = Column(Float, nullable=False)
    pdf_path = Column(String, nullable=True)
    metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    scan_session = relationship("ScanSession", back_populates="report")
    lembaga = relationship("Lembaga", back_populates="reports")
