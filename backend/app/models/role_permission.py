from sqlalchemy import Column, Integer, String
from app.db.database import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, index=True, nullable=False)
    permission_key = Column(String, index=True, nullable=False)
