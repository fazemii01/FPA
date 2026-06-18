from typing import Iterable, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import decode_access_token
from app.repositories.user import UserRepository
from app.models.user import User, UserRole
from app.models.role_permission import RolePermission

security = HTTPBearer()


def get_permissions_for_role(db: Session, role: UserRole) -> List[str]:
    if role == UserRole.SUPER_ADMIN:
        return ["CREATE_SESSION", "VIEW_HISTORY", "DELETE_SESSION", "GENERATE_REPORT", "MANAGE_USERS"]
    
    # Query database for configured permissions
    perms = db.query(RolePermission).filter(RolePermission.role == role.value).all()
    if perms:
        return [p.permission_key for p in perms]
        
    # Default fallback if table is empty or no mappings configured yet
    if role == UserRole.ADMIN:
        return ["CREATE_SESSION", "VIEW_HISTORY", "DELETE_SESSION", "GENERATE_REPORT", "MANAGE_USERS"]
    elif role == UserRole.STAFF:
        return ["CREATE_SESSION", "VIEW_HISTORY"]
    return []


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = UserRepository.get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    # Dynamically attach permissions list to the SQLAlchemy model instance
    user.permissions = get_permissions_for_role(db, user.role)

    return user


def require_role(*allowed_roles: UserRole):
    allowed: Iterable[UserRole] = allowed_roles or (UserRole.ADMIN, UserRole.STAFF)

    async def _enforcer(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {', '.join(r.value for r in allowed)}",
            )
        return current_user

    return _enforcer


def require_permission(permission_key: str):
    async def _enforcer(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role == UserRole.SUPER_ADMIN:
            return current_user
        if permission_key not in getattr(current_user, "permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: requires {permission_key}",
            )
        return current_user
    return _enforcer


require_admin = require_role(UserRole.ADMIN)
require_staff_or_admin = require_role(UserRole.ADMIN, UserRole.STAFF)
require_super_admin = require_role(UserRole.SUPER_ADMIN)

