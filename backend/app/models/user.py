from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from typing import Optional
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.database import Base


class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    STAFF = "staff"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(SQLEnum(UserRole, name="userrole", values_callable=lambda x: [e.value for e in x]), nullable=False, default=UserRole.STAFF)
    lembaga_id = Column(Integer, ForeignKey("lembaga.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lembaga = relationship("Lembaga", back_populates="users")

    scan_sessions = relationship(
        "ScanSession",
        back_populates="user",
        foreign_keys="ScanSession.user_id",
    )
    reviewed_sessions = relationship(
        "ScanSession",
        back_populates="reviewed_by",
        foreign_keys="ScanSession.reviewed_by_id",
    )

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def lembaga_name(self) -> Optional[str]:
        return self.lembaga.name if self.lembaga else None

    @property
    def lembaga_credits(self) -> Optional[int]:
        return self.lembaga.credits if self.lembaga else None

    @property
    def lembaga_type(self) -> Optional[str]:
        return self.lembaga.type if self.lembaga else None
