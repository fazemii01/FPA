from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.middleware.auth import require_super_admin
from app.models.user import User, UserRole
from app.models.lembaga import Lembaga
from app.models.payment_log import PaymentLog
from app.models.role_permission import RolePermission
from app.models.scan_session import ScanSession
from app.models.report import Report
from app.models.system_setting import SystemSetting

from app.schemas.user import UserCreate
from app.schemas.super_admin import (
    LembagaCreate,
    LembagaUpdate,
    LembagaResponse,
    TopUpRequest,
    PermissionMappingUpdate,
    PaymentLogResponse,
    UserAuditResponse,
    DashboardStatsResponse,
    SystemSettingResponse,
    SystemSettingsUpdate,
)

router = APIRouter(
    prefix="/super-admin",
    tags=["super-admin"],
    dependencies=[Depends(require_super_admin)],
)


@router.get("/lembaga", response_model=List[LembagaResponse])
def list_lembaga(db: Session = Depends(get_db)):
    """List all institutions (Lembaga) with user and report statistics."""
    lembaga_list = db.query(Lembaga).all()
    result = []
    for lem in lembaga_list:
        users_count = db.query(User).filter(User.lembaga_id == lem.id).count()
        reports_count = db.query(Report).filter(Report.lembaga_id == lem.id).count()
        result.append({
            "id": lem.id,
            "name": lem.name,
            "credits": lem.credits,
            "is_active": lem.is_active,
            "type": lem.type,
            "created_at": lem.created_at,
            "users_count": users_count,
            "reports_count": reports_count
        })
    return result


@router.post("/lembaga", response_model=LembagaResponse)
def create_lembaga(payload: LembagaCreate, db: Session = Depends(get_db)):
    """Create a new institution (Lembaga)."""
    existing = db.query(Lembaga).filter(Lembaga.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Nama lembaga sudah terdaftar")
    lem = Lembaga(
        name=payload.name,
        credits=payload.credits,
        is_active=payload.is_active,
        type=payload.type
    )
    db.add(lem)
    db.commit()
    db.refresh(lem)
    return {
        "id": lem.id,
        "name": lem.name,
        "credits": lem.credits,
        "is_active": lem.is_active,
        "type": lem.type,
        "created_at": lem.created_at,
        "users_count": 0,
        "reports_count": 0
    }


@router.put("/lembaga/{lembaga_id}", response_model=LembagaResponse)
def update_lembaga(lembaga_id: int, payload: LembagaUpdate, db: Session = Depends(get_db)):
    """Update institution properties."""
    lem = db.query(Lembaga).filter(Lembaga.id == lembaga_id).first()
    if not lem:
        raise HTTPException(status_code=404, detail="Lembaga tidak ditemukan")
    
    if payload.name is not None:
        existing = db.query(Lembaga).filter(Lembaga.name == payload.name, Lembaga.id != lembaga_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Nama lembaga sudah terdaftar")
        lem.name = payload.name
    if payload.credits is not None:
        lem.credits = payload.credits
    if payload.is_active is not None:
        lem.is_active = payload.is_active
    if payload.type is not None:
        lem.type = payload.type
        
    db.commit()
    db.refresh(lem)
    
    users_count = db.query(User).filter(User.lembaga_id == lem.id).count()
    reports_count = db.query(Report).filter(Report.lembaga_id == lem.id).count()
    return {
        "id": lem.id,
        "name": lem.name,
        "credits": lem.credits,
        "is_active": lem.is_active,
        "type": lem.type,
        "created_at": lem.created_at,
        "users_count": users_count,
        "reports_count": reports_count
    }


@router.post("/lembaga/{lembaga_id}/topup", response_model=LembagaResponse)
def topup_lembaga(lembaga_id: int, payload: TopUpRequest, db: Session = Depends(get_db)):
    """Top up institution credits and log a payment record."""
    lem = db.query(Lembaga).filter(Lembaga.id == lembaga_id).with_for_update().first()
    if not lem:
        raise HTTPException(status_code=404, detail="Lembaga tidak ditemukan")
    
    lem.credits += payload.credits
    log = PaymentLog(
        lembaga_id=lembaga_id,
        amount=payload.amount,
        credits_added=payload.credits,
        reference_no=payload.reference_no,
        status="success"
    )
    db.add(log)
    db.commit()
    db.refresh(lem)
    
    users_count = db.query(User).filter(User.lembaga_id == lem.id).count()
    reports_count = db.query(Report).filter(Report.lembaga_id == lem.id).count()
    return {
        "id": lem.id,
        "name": lem.name,
        "credits": lem.credits,
        "is_active": lem.is_active,
        "created_at": lem.created_at,
        "users_count": users_count,
        "reports_count": reports_count
    }


@router.get("/users", response_model=List[UserAuditResponse])
def list_users(db: Session = Depends(get_db)):
    """List all registered users globally with their institution details."""
    users = db.query(User).all()
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "lembaga_id": u.lembaga_id,
            "lembaga_name": u.lembaga.name if u.lembaga else None,
            "is_active": u.is_active,
            "created_at": u.created_at
        })
    return result


@router.post("/users", response_model=UserAuditResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user (Super Admin only)."""
    from app.repositories.user import UserRepository
    existing = UserRepository.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar",
        )
    
    db_user = UserRepository.create_user(db, payload)
    from app.middleware.auth import get_permissions_for_role
    db_user.permissions = get_permissions_for_role(db, db_user.role)
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "full_name": db_user.full_name,
        "role": db_user.role.value,
        "lembaga_id": db_user.lembaga_id,
        "lembaga_name": db_user.lembaga.name if db_user.lembaga else None,
        "is_active": db_user.is_active,
        "created_at": db_user.created_at
    }


@router.put("/users/{user_id}", response_model=UserAuditResponse)
def update_user(user_id: int, payload: dict, db: Session = Depends(get_db)):
    """Audit user: Edit details, change role, institution link, active status, or password."""
    from app.core.security import get_password_hash
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    if "full_name" in payload:
        u.full_name = payload["full_name"]
    if "email" in payload:
        existing = db.query(User).filter(User.email == payload["email"], User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email sudah terdaftar oleh pengguna lain")
        u.email = payload["email"]
    if "role" in payload:
        u.role = UserRole(payload["role"])
    if "lembaga_id" in payload:
        u.lembaga_id = payload["lembaga_id"]
    if "is_active" in payload:
        u.is_active = payload["is_active"]
    if "password" in payload and payload["password"]:
        u.hashed_password = get_password_hash(payload["password"])
        
    db.commit()
    db.refresh(u)
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role.value,
        "lembaga_id": u.lembaga_id,
        "lembaga_name": u.lembaga.name if u.lembaga else None,
        "is_active": u.is_active,
        "created_at": u.created_at
    }


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user, cascading scan session deletions and clearing reviewer associations."""
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
        
    from app.repositories.scan import ScanSessionRepository
    from app.models.scan_session import ScanSession
    
    # 1. Clean up scan sessions created by this user
    sessions = db.query(ScanSession).filter(ScanSession.user_id == user_id).all()
    for s in sessions:
        ScanSessionRepository.delete_session(db, s.id)
        
    # 2. Clear reviewed_by_id reference on sessions reviewed by this user
    db.query(ScanSession).filter(ScanSession.reviewed_by_id == user_id).update(
        {ScanSession.reviewed_by_id: None}, 
        synchronize_session=False
    )
    
    # 3. Delete the user itself
    db.delete(u)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/permissions")
def get_permissions(db: Session = Depends(get_db)):
    """Get active role to permission mappings."""
    mappings = db.query(RolePermission).all()
    result = {}
    for m in mappings:
        if m.role not in result:
            result[m.role] = []
        result[m.role].append(m.permission_key)
    
    # Fill in empty arrays for defaults if missing
    for role in ["admin", "staff"]:
        if role not in result:
            result[role] = []
    return result


@router.post("/permissions")
def update_permissions(payload: List[PermissionMappingUpdate], db: Session = Depends(get_db)):
    """Overwrite role to permission mappings dynamically."""
    for mapping in payload:
        # Prevent configuring permissions for super_admin directly (hardcoded to all access)
        if mapping.role == "super_admin":
            continue
        db.query(RolePermission).filter(RolePermission.role == mapping.role).delete()
        for key in mapping.permissions:
            db.add(RolePermission(role=mapping.role, permission_key=key))
    db.commit()
    return {"status": "success"}


@router.get("/payments", response_model=List[PaymentLogResponse])
def list_payments(db: Session = Depends(get_db)):
    """Get a log of all credit purchase transactions."""
    logs = db.query(PaymentLog).order_by(PaymentLog.created_at.desc()).all()
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "lembaga_id": log.lembaga_id,
            "lembaga_name": log.lembaga.name if log.lembaga else f"ID: {log.lembaga_id}",
            "amount": log.amount,
            "credits_added": log.credits_added,
            "status": log.status,
            "reference_no": log.reference_no,
            "created_at": log.created_at
        })
    return result


@router.get("/dashboard-stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get overall aggregated overview statistics for the main dashboard."""
    from sqlalchemy import func
    total_lembaga = db.query(Lembaga).count()
    total_credits = db.query(func.sum(Lembaga.credits)).scalar() or 0
    total_users = db.query(User).count()
    total_scans = db.query(ScanSession).count()
    total_reports = db.query(Report).count()
    
    recent = db.query(ScanSession).order_by(ScanSession.created_at.desc()).limit(5).all()
    recent_sessions = [{
        "id": s.id,
        "participant_name": s.participant_name,
        "lembaga_name": s.lembaga.name if s.lembaga else "None",
        "status": s.status.value,
        "created_at": s.created_at.isoformat()
    } for s in recent]
    
    summary = db.query(Lembaga).order_by(Lembaga.credits.desc()).limit(5).all()
    credit_summary = [{
        "name": l.name,
        "credits": l.credits
    } for l in summary]
    
    return {
        "total_lembaga": total_lembaga,
        "total_credits": total_credits,
        "total_users": total_users,
        "total_scans": total_scans,
        "total_reports": total_reports,
        "recent_sessions": recent_sessions,
        "credit_summary": credit_summary
    }


@router.get("/settings", response_model=List[SystemSettingResponse])
def get_settings(db: Session = Depends(get_db)):
    """Retrieve all system settings."""
    return db.query(SystemSetting).all()


@router.put("/settings")
def update_settings(payload: SystemSettingsUpdate, db: Session = Depends(get_db)):
    """Bulk update system settings."""
    settings = {
        "topup_bulk_options": payload.topup_bulk_options,
        "price_umum": str(payload.price_umum),
        "price_partner": str(payload.price_partner),
    }
    for key, val in settings.items():
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if not setting:
            setting = SystemSetting(key=key, value=val)
            db.add(setting)
        else:
            setting.value = val
    db.commit()
    return {"status": "success"}
