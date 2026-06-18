from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Lembaga(Base):
    __tablename__ = "lembaga"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    credits = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="lembaga")
    scan_sessions = relationship("ScanSession", back_populates="lembaga")
    reports = relationship("Report", back_populates="lembaga")
    payment_logs = relationship("PaymentLog", back_populates="lembaga")
    invoices = relationship("Invoice", back_populates="lembaga", cascade="all, delete-orphan")
