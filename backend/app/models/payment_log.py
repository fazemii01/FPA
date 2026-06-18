from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class PaymentLog(Base):
    __tablename__ = "payment_logs"

    id = Column(Integer, primary_key=True, index=True)
    lembaga_id = Column(Integer, ForeignKey("lembaga.id"), nullable=False)
    amount = Column(Float, nullable=False)
    credits_added = Column(Integer, nullable=False)
    status = Column(String, default="success", nullable=False)
    reference_no = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    lembaga = relationship("Lembaga", back_populates="payment_logs")
