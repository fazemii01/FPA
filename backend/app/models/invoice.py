from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(50), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(20), unique=True, index=True, nullable=False)
    lembaga_id = Column(Integer, ForeignKey("lembaga.id"), nullable=False)
    client_name = Column(String(120), nullable=False)
    description = Column(String(255), nullable=False)
    credits = Column(Integer, nullable=False)
    discount = Column(Float, default=0.0, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    payment_proof_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lembaga = relationship("Lembaga", back_populates="invoices")
