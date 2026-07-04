from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.middleware.auth import require_super_admin, get_current_user, require_admin_pusat
from app.models.user import User, UserRole
from app.models.lembaga import Lembaga
from app.models.payment_log import PaymentLog
from app.models.role_permission import RolePermission
from app.models.scan_session import ScanSession
from app.models.report import Report
from app.models.system_setting import SystemSetting
from app.models.wilayah import Wilayah

from app.schemas.user import UserCreate, UserRoleEnum
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
from app.schemas.wilayah import WilayahCreate, WilayahResponse, WilayahTopUp

router = APIRouter(
    prefix="/super-admin",
    tags=["super-admin"],
    dependencies=[Depends(require_super_admin)],
)


@router.get("/lembaga", response_model=List[LembagaResponse])
def list_lembaga(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all institutions (Lembaga) with user and report statistics."""
    if current_user.role == UserRole.SUPER_ADMIN:
        lembaga_list = db.query(Lembaga).filter(Lembaga.wilayah_id == current_user.wilayah_id).all()
    else:
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
            "wilayah_id": lem.wilayah_id,
            "wilayah_name": lem.wilayah.name if lem.wilayah else None,
            "created_at": lem.created_at,
            "users_count": users_count,
            "reports_count": reports_count
        })
    return result


@router.post("/lembaga", response_model=LembagaResponse)
def create_lembaga(payload: LembagaCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new institution (Lembaga)."""
    existing = db.query(Lembaga).filter(Lembaga.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Nama lembaga sudah terdaftar")
    
    wilayah_id = current_user.wilayah_id if current_user.role == UserRole.SUPER_ADMIN else payload.wilayah_id
    
    lem = Lembaga(
        name=payload.name,
        credits=payload.credits,
        is_active=payload.is_active,
        type=payload.type,
        wilayah_id=wilayah_id
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
        "wilayah_id": lem.wilayah_id,
        "wilayah_name": lem.wilayah.name if lem.wilayah else None,
        "created_at": lem.created_at,
        "users_count": 0,
        "reports_count": 0
    }


@router.put("/lembaga/{lembaga_id}", response_model=LembagaResponse)
def update_lembaga(lembaga_id: int, payload: LembagaUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update institution properties."""
    lem = db.query(Lembaga).filter(Lembaga.id == lembaga_id).first()
    if not lem:
        raise HTTPException(status_code=404, detail="Lembaga tidak ditemukan")
    
    if current_user.role == UserRole.SUPER_ADMIN and lem.wilayah_id != current_user.wilayah_id:
        raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke lembaga di wilayah lain")
        
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
    if payload.wilayah_id is not None and current_user.role == UserRole.ADMIN_PUSAT:
        lem.wilayah_id = payload.wilayah_id
        
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
        "wilayah_id": lem.wilayah_id,
        "wilayah_name": lem.wilayah.name if lem.wilayah else None,
        "created_at": lem.created_at,
        "users_count": users_count,
        "reports_count": reports_count
    }


@router.post("/lembaga/{lembaga_id}/topup", response_model=LembagaResponse)
def topup_lembaga(lembaga_id: int, payload: TopUpRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Top up institution credits and log a payment record."""
    lem = db.query(Lembaga).filter(Lembaga.id == lembaga_id).with_for_update().first()
    if not lem:
        raise HTTPException(status_code=404, detail="Lembaga tidak ditemukan")
    
    if current_user.role == UserRole.SUPER_ADMIN:
        if lem.wilayah_id != current_user.wilayah_id:
            raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke lembaga di wilayah lain")
        
        # Check if wilayah has enough credits
        wilayah = current_user.wilayah
        if not wilayah or wilayah.credits < payload.credits:
            raise HTTPException(
                status_code=400,
                detail="Kredit wilayah tidak cukup, silakan hubungi admin pusat untuk top up"
            )
        
        # Deduct from wilayah, add to lembaga
        wilayah.credits -= payload.credits
        lem.credits += payload.credits
        
        log = PaymentLog(
            lembaga_id=lembaga_id,
            wilayah_id=current_user.wilayah_id,
            amount=payload.amount,
            credits_added=payload.credits,
            reference_no=payload.reference_no,
            status="success"
        )
    else:
        # admin_pusat
        lem.credits += payload.credits
        log = PaymentLog(
            lembaga_id=lembaga_id,
            wilayah_id=lem.wilayah_id,
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
        "type": lem.type,
        "wilayah_id": lem.wilayah_id,
        "wilayah_name": lem.wilayah.name if lem.wilayah else None,
        "created_at": lem.created_at,
        "users_count": users_count,
        "reports_count": reports_count
    }


@router.get("/users", response_model=List[UserAuditResponse])
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all registered users globally with their institution details."""
    if current_user.role == UserRole.SUPER_ADMIN:
        # Show users belonging to institutions in super admin's wilayah
        users = db.query(User).filter(User.lembaga.has(Lembaga.wilayah_id == current_user.wilayah_id)).all()
    else:
        # admin_pusat
        users = db.query(User).all()
        
    result = []
    for u in users:
        w_id = u.wilayah_id or (u.lembaga.wilayah_id if u.lembaga else None)
        w_name = (u.wilayah.name if u.wilayah else None) or (u.lembaga.wilayah.name if u.lembaga and u.lembaga.wilayah else None)
        result.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "lembaga_id": u.lembaga_id,
            "lembaga_name": u.lembaga.name if u.lembaga else None,
            "wilayah_id": w_id,
            "wilayah_name": w_name,
            "is_active": u.is_active,
            "created_at": u.created_at
        })
    return result


@router.post("/users", response_model=UserAuditResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new user (Super Admin only)."""
    from app.repositories.user import UserRepository
    existing = UserRepository.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar",
        )
        
    if current_user.role == UserRole.SUPER_ADMIN:
        # Enforce that the target lembaga is in super admin's wilayah
        if not payload.lembaga_id:
            raise HTTPException(status_code=400, detail="Lembaga harus diisi")
        lem = db.query(Lembaga).filter(Lembaga.id == payload.lembaga_id).first()
        if not lem or lem.wilayah_id != current_user.wilayah_id:
            raise HTTPException(status_code=403, detail="Anda hanya dapat membuat pengguna untuk lembaga di wilayah Anda")
        
        # Enforce restricted role assignment
        if payload.role in (UserRoleEnum.SUPER_ADMIN, UserRoleEnum.ADMIN_PUSAT):
            raise HTTPException(status_code=403, detail="Anda tidak dapat membuat pengguna dengan peran tersebut")
            
        payload.wilayah_id = None
    else:
        # admin_pusat
        if payload.role == UserRoleEnum.SUPER_ADMIN and not payload.wilayah_id:
            raise HTTPException(status_code=400, detail="Super Admin harus dikaitkan dengan Wilayah")
    
    db_user = UserRepository.create_user(db, payload)
    from app.middleware.auth import get_permissions_for_role
    db_user.permissions = get_permissions_for_role(db, db_user.role)
    
    w_id = db_user.wilayah_id or (db_user.lembaga.wilayah_id if db_user.lembaga else None)
    w_name = (db_user.wilayah.name if db_user.wilayah else None) or (db_user.lembaga.wilayah.name if db_user.lembaga and db_user.lembaga.wilayah else None)
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "full_name": db_user.full_name,
        "role": db_user.role.value,
        "lembaga_id": db_user.lembaga_id,
        "lembaga_name": db_user.lembaga.name if db_user.lembaga else None,
        "wilayah_id": w_id,
        "wilayah_name": w_name,
        "is_active": db_user.is_active,
        "created_at": db_user.created_at
    }


@router.put("/users/{user_id}", response_model=UserAuditResponse)
def update_user(user_id: int, payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Audit user: Edit details, change role, institution link, active status, or password."""
    from app.core.security import get_password_hash
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
        
    if current_user.role == UserRole.SUPER_ADMIN:
        # Check if target user belongs to super admin's wilayah
        if not u.lembaga or u.lembaga.wilayah_id != current_user.wilayah_id:
            raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke pengguna di wilayah lain")
        if u.role in (UserRole.SUPER_ADMIN, UserRole.ADMIN_PUSAT):
            raise HTTPException(status_code=403, detail="Anda tidak dapat mengubah pengguna dengan peran ini")
            
        # Ensure new role is restricted
        if "role" in payload and payload["role"] in (UserRole.SUPER_ADMIN.value, UserRole.ADMIN_PUSAT.value):
            raise HTTPException(status_code=403, detail="Anda tidak dapat menetapkan peran tersebut")
            
        # Ensure new lembaga is in same wilayah
        if "lembaga_id" in payload and payload["lembaga_id"]:
            lem = db.query(Lembaga).filter(Lembaga.id == payload["lembaga_id"]).first()
            if not lem or lem.wilayah_id != current_user.wilayah_id:
                raise HTTPException(status_code=403, detail="Lembaga baru harus berada di wilayah Anda")
    
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
    if "wilayah_id" in payload and current_user.role == UserRole.ADMIN_PUSAT:
        u.wilayah_id = payload["wilayah_id"]
    if "is_active" in payload:
        u.is_active = payload["is_active"]
    if "password" in payload and payload["password"]:
        u.hashed_password = get_password_hash(payload["password"])
        
    db.commit()
    db.refresh(u)
    
    w_id = u.wilayah_id or (u.lembaga.wilayah_id if u.lembaga else None)
    w_name = (u.wilayah.name if u.wilayah else None) or (u.lembaga.wilayah.name if u.lembaga and u.lembaga.wilayah else None)
    
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role.value,
        "lembaga_id": u.lembaga_id,
        "lembaga_name": u.lembaga.name if u.lembaga else None,
        "wilayah_id": w_id,
        "wilayah_name": w_name,
        "is_active": u.is_active,
        "created_at": u.created_at
    }


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete user, cascading scan session deletions and clearing reviewer associations."""
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
        
    if current_user.role == UserRole.SUPER_ADMIN:
        if not u.lembaga or u.lembaga.wilayah_id != current_user.wilayah_id:
            raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke pengguna di wilayah lain")
        if u.role in (UserRole.SUPER_ADMIN, UserRole.ADMIN_PUSAT):
            raise HTTPException(status_code=403, detail="Anda tidak dapat menghapus pengguna dengan peran ini")
            
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
def get_permissions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get active role to permission mappings. (Admin Pusat only)"""
    if current_user.role != UserRole.ADMIN_PUSAT:
        raise HTTPException(status_code=403, detail="Hanya Admin Pusat yang dapat melihat pemetaan izin")
        
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
def update_permissions(payload: List[PermissionMappingUpdate], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Overwrite role to permission mappings dynamically. (Admin Pusat only)"""
    if current_user.role != UserRole.ADMIN_PUSAT:
        raise HTTPException(status_code=403, detail="Hanya Admin Pusat yang dapat mengubah pemetaan izin")
        
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
def list_payments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a log of all credit purchase transactions."""
    if current_user.role == UserRole.SUPER_ADMIN:
        logs = db.query(PaymentLog).filter(PaymentLog.wilayah_id == current_user.wilayah_id).order_by(PaymentLog.created_at.desc()).all()
    else:
        logs = db.query(PaymentLog).order_by(PaymentLog.created_at.desc()).all()
        
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "lembaga_id": log.lembaga_id,
            "lembaga_name": log.lembaga.name if log.lembaga else (f"ID: {log.lembaga_id}" if log.lembaga_id else None),
            "wilayah_id": log.wilayah_id,
            "wilayah_name": log.wilayah.name if log.wilayah else None,
            "amount": log.amount,
            "credits_added": log.credits_added,
            "status": log.status,
            "reference_no": log.reference_no,
            "created_at": log.created_at
        })
    return result


@router.get("/dashboard-stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get overall aggregated overview statistics for the main dashboard."""
    from sqlalchemy import func
    
    if current_user.role == UserRole.SUPER_ADMIN:
        w_id = current_user.wilayah_id
        total_lembaga = db.query(Lembaga).filter(Lembaga.wilayah_id == w_id).count()
        total_credits = db.query(func.sum(Lembaga.credits)).filter(Lembaga.wilayah_id == w_id).scalar() or 0
        total_users = db.query(User).filter(User.lembaga.has(Lembaga.wilayah_id == w_id)).count()
        total_scans = db.query(ScanSession).filter(ScanSession.lembaga.has(Lembaga.wilayah_id == w_id)).count()
        total_reports = db.query(Report).filter(Report.lembaga.has(Lembaga.wilayah_id == w_id)).count()
        
        recent = db.query(ScanSession).filter(ScanSession.lembaga.has(Lembaga.wilayah_id == w_id)).order_by(ScanSession.created_at.desc()).limit(5).all()
        summary = db.query(Lembaga).filter(Lembaga.wilayah_id == w_id).order_by(Lembaga.credits.desc()).limit(5).all()
        wilayah_credits = current_user.wilayah.credits if current_user.wilayah else 0
    else:
        # admin_pusat
        total_lembaga = db.query(Lembaga).count()
        total_credits = db.query(func.sum(Lembaga.credits)).scalar() or 0
        total_users = db.query(User).count()
        total_scans = db.query(ScanSession).count()
        total_reports = db.query(Report).count()
        
        recent = db.query(ScanSession).order_by(ScanSession.created_at.desc()).limit(5).all()
        summary = db.query(Lembaga).order_by(Lembaga.credits.desc()).limit(5).all()
        wilayah_credits = None
        
    recent_sessions = [{
        "id": s.id,
        "participant_name": s.participant_name,
        "lembaga_name": s.lembaga.name if s.lembaga else "None",
        "status": s.status.value,
        "created_at": s.created_at.isoformat()
    } for s in recent]
    
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
        "credit_summary": credit_summary,
        "wilayah_credits": wilayah_credits
    }


@router.get("/settings", response_model=List[SystemSettingResponse])
def get_settings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve all system settings. (Admin Pusat only)"""
    if current_user.role != UserRole.ADMIN_PUSAT:
        raise HTTPException(status_code=403, detail="Hanya Admin Pusat yang dapat melihat pengaturan")
    return db.query(SystemSetting).all()


@router.put("/settings")
def update_settings(payload: SystemSettingsUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Bulk update system settings. (Admin Pusat only)"""
    if current_user.role != UserRole.ADMIN_PUSAT:
        raise HTTPException(status_code=403, detail="Hanya Admin Pusat yang dapat mengubah pengaturan")
        
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


# ----------------- WILAYAH ENDPOINTS (Admin Pusat Only) -----------------

@router.get("/wilayah", response_model=List[WilayahResponse], dependencies=[Depends(require_admin_pusat)])
def list_wilayah(db: Session = Depends(get_db)):
    """List all regions/cities (Wilayah) with their stats."""
    wilayah_list = db.query(Wilayah).all()
    result = []
    for w in wilayah_list:
        # Find super admin assigned to this wilayah
        super_admin = db.query(User).filter(User.wilayah_id == w.id, User.role == UserRole.SUPER_ADMIN).first()
        lembaga_count = db.query(Lembaga).filter(Lembaga.wilayah_id == w.id).count()
        result.append({
            "id": w.id,
            "name": w.name,
            "credits": w.credits,
            "created_at": w.created_at,
            "updated_at": w.updated_at,
            "lembaga_count": lembaga_count,
            "super_admin_email": super_admin.email if super_admin else None,
            "super_admin_name": super_admin.full_name if super_admin else None
        })
    return result


@router.post("/wilayah", response_model=WilayahResponse, dependencies=[Depends(require_admin_pusat)])
def create_wilayah(payload: WilayahCreate, db: Session = Depends(get_db)):
    """Create a new region/city (Wilayah)."""
    existing = db.query(Wilayah).filter(Wilayah.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Wilayah sudah terdaftar")
        
    w = Wilayah(
        name=payload.name,
        credits=payload.credits
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    
    return {
        "id": w.id,
        "name": w.name,
        "credits": w.credits,
        "created_at": w.created_at,
        "updated_at": w.updated_at,
        "lembaga_count": 0,
        "super_admin_email": None,
        "super_admin_name": None
    }


@router.put("/wilayah/{wilayah_id}", response_model=WilayahResponse, dependencies=[Depends(require_admin_pusat)])
def update_wilayah(wilayah_id: int, payload: WilayahCreate, db: Session = Depends(get_db)):
    """Update a Wilayah name/credits."""
    w = db.query(Wilayah).filter(Wilayah.id == wilayah_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Wilayah tidak ditemukan")
        
    existing = db.query(Wilayah).filter(Wilayah.name == payload.name, Wilayah.id != wilayah_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Nama wilayah sudah digunakan")
        
    w.name = payload.name
    w.credits = payload.credits
    db.commit()
    db.refresh(w)
    
    super_admin = db.query(User).filter(User.wilayah_id == w.id, User.role == UserRole.SUPER_ADMIN).first()
    lembaga_count = db.query(Lembaga).filter(Lembaga.wilayah_id == w.id).count()
    
    return {
        "id": w.id,
        "name": w.name,
        "credits": w.credits,
        "created_at": w.created_at,
        "updated_at": w.updated_at,
        "lembaga_count": lembaga_count,
        "super_admin_email": super_admin.email if super_admin else None,
        "super_admin_name": super_admin.full_name if super_admin else None
    }


@router.post("/wilayah/{wilayah_id}/topup", response_model=WilayahResponse, dependencies=[Depends(require_admin_pusat)])
def topup_wilayah(wilayah_id: int, payload: WilayahTopUp, db: Session = Depends(get_db)):
    """Top up credits for a Wilayah directly."""
    w = db.query(Wilayah).filter(Wilayah.id == wilayah_id).with_for_update().first()
    if not w:
        raise HTTPException(status_code=404, detail="Wilayah tidak ditemukan")
        
    w.credits += payload.credits
    
    # Log the payment
    log = PaymentLog(
        wilayah_id=wilayah_id,
        amount=0.0,  # Direct admin topup has 0.0 amount or custom if needed
        credits_added=payload.credits,
        status="success",
        reference_no="DIRECT-WILAYAH-TOPUP"
    )
    db.add(log)
    db.commit()
    db.refresh(w)
    
    super_admin = db.query(User).filter(User.wilayah_id == w.id, User.role == UserRole.SUPER_ADMIN).first()
    lembaga_count = db.query(Lembaga).filter(Lembaga.wilayah_id == w.id).count()
    
    return {
        "id": w.id,
        "name": w.name,
        "credits": w.credits,
        "created_at": w.created_at,
        "updated_at": w.updated_at,
        "lembaga_count": lembaga_count,
        "super_admin_email": super_admin.email if super_admin else None,
        "super_admin_name": super_admin.full_name if super_admin else None
    }


@router.delete("/wilayah/{wilayah_id}", dependencies=[Depends(require_admin_pusat)])
def delete_wilayah(wilayah_id: int, db: Session = Depends(get_db)):
    """Delete a Wilayah."""
    w = db.query(Wilayah).filter(Wilayah.id == wilayah_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Wilayah tidak ditemukan")
        
    # Unlink users and lembaga
    db.query(User).filter(User.wilayah_id == wilayah_id).update({User.wilayah_id: None})
    db.query(Lembaga).filter(Lembaga.wilayah_id == wilayah_id).update({Lembaga.wilayah_id: None})
    
    db.delete(w)
    db.commit()
    return {"status": "success"}
