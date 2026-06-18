from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.repositories.user import UserRepository
from app.core.security import create_access_token
from app.middleware.auth import get_current_user
from app.models.user import User, UserRole
from app.core.security import decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    if UserRepository.count_users(db) == 0:
        user.role = UserRole.ADMIN
    else:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        payload = decode_access_token(authorization.split(" ", 1)[1])
        if payload is None or payload.get("sub") is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        current_user = UserRepository.get_user_by_id(db, int(payload["sub"]))
        if current_user is None or current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires role: admin")
        
        # If the creating admin is affiliated with a lembaga, the new user inherits it
        if current_user.lembaga_id is not None:
            user.lembaga_id = current_user.lembaga_id

    existing_user = UserRepository.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    db_user = UserRepository.create_user(db, user)
    from app.middleware.auth import get_permissions_for_role
    db_user.permissions = get_permissions_for_role(db, db_user.role)
    return db_user


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = UserRepository.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    from app.middleware.auth import get_permissions_for_role
    permissions = get_permissions_for_role(db, user.role)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.value,
        "permissions": permissions,
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
