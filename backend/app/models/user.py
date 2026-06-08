from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.database import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(SQLEnum(UserRole, name="userrole", values_callable=lambda x: [e.value for e in x]), nullable=False, default=UserRole.STAFF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
