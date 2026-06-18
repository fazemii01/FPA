from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password
from app.schemas.user import UserCreate


class UserRepository:
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            role=UserRole(user.role.value),
            lembaga_id=user.lembaga_id,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def count_users(db: Session) -> int:
        return db.query(User).count()

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = UserRepository.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
