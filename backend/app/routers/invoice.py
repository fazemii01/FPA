from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, Response
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.database import get_db
from app.middleware.auth import require_super_admin, get_current_user
from app.models.invoice import Invoice
from app.models.lembaga import Lembaga
from app.models.payment_log import PaymentLog
from app.models.system_setting import SystemSetting
from app.models.user import User, UserRole
from app.models.wilayah import Wilayah
from app.schemas.invoice import InvoiceCreate, InvoiceResponse
from app.storage.minio_service import MinIOService

router = APIRouter(
    prefix="/invoices",
    tags=["invoices"],
)

minio_service = MinIOService()

import random
import string

def generate_invoice_code(db: Session) -> str:
    while True:
        # Generate 8 random uppercase alphanumeric characters
        chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        code = f"INV-{chars}"
        # Check uniqueness
        exists = db.query(Invoice).filter(Invoice.code == code).first()
        if not exists:
            return code

# ----------------- ADMIN ENDPOINTS (Requires Super Admin) -----------------

@router.post("", response_model=InvoiceResponse)
def create_invoice(payload: InvoiceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new top-up invoice (Super Admin / Admin Pusat)."""
    if payload.lembaga_id:
        # Verify Lembaga exists
        lembaga = db.query(Lembaga).filter(Lembaga.id == payload.lembaga_id).first()
        if not lembaga:
            raise HTTPException(status_code=404, detail="Lembaga tidak ditemukan")
            
        if current_user.role == UserRole.SUPER_ADMIN and lembaga.wilayah_id != current_user.wilayah_id:
            raise HTTPException(status_code=403, detail="Anda hanya dapat membuat invoice untuk lembaga di wilayah Anda")
            
        # Calculate amount dynamically from SystemSetting
        price_key = "price_partner" if lembaga.type == "partner" else "price_umum"
        setting = db.query(SystemSetting).filter(SystemSetting.key == price_key).first()
        price_per_credit = float(setting.value) if setting else (95000.0 if lembaga.type == "partner" else 125000.0)
        wilayah_id = lembaga.wilayah_id
    else:
        # Super Admin regional topup request from Admin Pusat
        wilayah_id = current_user.wilayah_id if current_user.role == UserRole.SUPER_ADMIN else payload.wilayah_id
        if not wilayah_id:
            raise HTTPException(status_code=400, detail="Wilayah harus ditentukan untuk top-up regional")
            
        wilayah = db.query(Wilayah).filter(Wilayah.id == wilayah_id).first()
        if not wilayah:
            raise HTTPException(status_code=404, detail="Wilayah tidak ditemukan")
            
        # Default price for regional credits topup (use price_partner)
        setting = db.query(SystemSetting).filter(SystemSetting.key == "price_partner").first()
        price_per_credit = float(setting.value) if setting else 95000.0
        
    subtotal = payload.credits * price_per_credit
    total_amount = subtotal - payload.discount
    if total_amount < 0:
        total_amount = 0.0

    inv_code = generate_invoice_code(db)
    inv = Invoice(
        lembaga_id=payload.lembaga_id,
        wilayah_id=wilayah_id,
        client_name=payload.client_name,
        description=payload.description,
        credits=payload.credits,
        discount=payload.discount,
        total_amount=total_amount,
        status="pending",
        code=inv_code,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    
    # Map relation fields
    res = InvoiceResponse.model_validate(inv)
    res.lembaga_name = inv.lembaga.name if inv.lembaga else None
    res.wilayah_name = inv.wilayah.name if inv.wilayah else None
    return res


@router.get("", response_model=List[InvoiceResponse])
def list_invoices(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all invoices for admin/super admin dashboard."""
    if current_user.role == UserRole.SUPER_ADMIN:
        invoices = db.query(Invoice).filter(Invoice.wilayah_id == current_user.wilayah_id).order_by(Invoice.created_at.desc()).all()
    else:
        invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
        
    result = []
    for inv in invoices:
        res = InvoiceResponse.model_validate(inv)
        res.lembaga_name = inv.lembaga.name if inv.lembaga else None
        res.wilayah_name = inv.wilayah.name if inv.wilayah else None
        if inv.payment_proof_path:
            res.payment_proof_url = f"{str(request.base_url).rstrip('/')}/invoices/public/{inv.uuid}/proof"
        result.append(res)
    return result


@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete an invoice."""
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
        
    if current_user.role == UserRole.SUPER_ADMIN and inv.wilayah_id != current_user.wilayah_id:
        raise HTTPException(status_code=403, detail="Anda tidak memiliki akses untuk menghapus invoice wilayah lain")
    
    # Delete payment proof from minio if exists
    if inv.payment_proof_path:
        try:
            minio_service.delete_fingerprint(inv.payment_proof_path)
        except Exception:
            pass
            
    db.delete(inv)
    db.commit()
    return {"status": "success"}


@router.post("/{invoice_id}/approve", response_model=InvoiceResponse)
def approve_invoice(invoice_id: int, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Approve invoice payment, add credits to institution/wilayah, and log the transaction."""
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).with_for_update().first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
        
    if inv.status == "success":
        raise HTTPException(status_code=400, detail="Invoice sudah lunas")
        
    if current_user.role == UserRole.SUPER_ADMIN:
        if inv.wilayah_id != current_user.wilayah_id:
            raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke invoice wilayah lain")
        if not inv.lembaga_id:
            raise HTTPException(status_code=403, detail="Hanya Admin Pusat yang dapat menyetujui invoice top-up wilayah")
            
        lembaga = db.query(Lembaga).filter(Lembaga.id == inv.lembaga_id).with_for_update().first()
        if not lembaga:
            raise HTTPException(status_code=404, detail="Lembaga dari invoice tidak ditemukan")
            
        # Verify regional credits
        wilayah = current_user.wilayah
        if not wilayah or wilayah.credits < inv.credits:
            raise HTTPException(
                status_code=400,
                detail="Kredit wilayah tidak cukup, silakan hubungi admin pusat untuk top up"
            )
            
        # Transactional update: deduct from super admin's wilayah, add to lembaga
        wilayah.credits -= inv.credits
        lembaga.credits += inv.credits
        
        log = PaymentLog(
            lembaga_id=inv.lembaga_id,
            wilayah_id=current_user.wilayah_id,
            amount=inv.total_amount,
            credits_added=inv.credits,
            reference_no=inv.code,
            status="success"
        )
    else:
        # admin_pusat
        if inv.lembaga_id:
            # Direct institution topup
            lembaga = db.query(Lembaga).filter(Lembaga.id == inv.lembaga_id).with_for_update().first()
            if not lembaga:
                raise HTTPException(status_code=404, detail="Lembaga dari invoice tidak ditemukan")
            lembaga.credits += inv.credits
            log = PaymentLog(
                lembaga_id=inv.lembaga_id,
                wilayah_id=inv.wilayah_id,
                amount=inv.total_amount,
                credits_added=inv.credits,
                reference_no=inv.code,
                status="success"
            )
        else:
            # Super Admin regional topup request
            wilayah = db.query(Wilayah).filter(Wilayah.id == inv.wilayah_id).with_for_update().first()
            if not wilayah:
                raise HTTPException(status_code=404, detail="Wilayah dari invoice tidak ditemukan")
            wilayah.credits += inv.credits
            log = PaymentLog(
                lembaga_id=None,
                wilayah_id=inv.wilayah_id,
                amount=inv.total_amount,
                credits_added=inv.credits,
                reference_no=inv.code,
                status="success"
            )
            
    db.add(log)
    inv.status = "success"
    db.commit()
    db.refresh(inv)
    
    res = InvoiceResponse.model_validate(inv)
    res.lembaga_name = inv.lembaga.name if inv.lembaga else None
    res.wilayah_name = inv.wilayah.name if inv.wilayah else None
    if inv.payment_proof_path:
        res.payment_proof_url = f"{str(request.base_url).rstrip('/')}/invoices/public/{inv.uuid}/proof"
    return res


# ----------------- PUBLIC ENDPOINTS -----------------

@router.get("/public/{uuid_str}", response_model=InvoiceResponse)
def get_public_invoice(uuid_str: str, request: Request, db: Session = Depends(get_db)):
    """Retrieve details of a public invoice (anyone can access)."""
    inv = db.query(Invoice).filter(Invoice.uuid == uuid_str).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
        
    res = InvoiceResponse.model_validate(inv)
    res.lembaga_name = inv.lembaga.name if inv.lembaga else None
    
    if inv.payment_proof_path:
        res.payment_proof_url = f"{str(request.base_url).rstrip('/')}/invoices/public/{inv.uuid}/proof"
            
    return res


@router.post("/public/{uuid_str}/upload-proof", response_model=InvoiceResponse)
async def upload_proof(uuid_str: str, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload payment proof for an invoice (anyone can access)."""
    inv = db.query(Invoice).filter(Invoice.uuid == uuid_str).with_for_update().first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
        
    if inv.status == "success":
        raise HTTPException(status_code=400, detail="Invoice sudah lunas")
        
    # Read file data
    file_data = await file.read()
    
    # Upload to MinIO under receipts/ prefix
    filename = file.filename or "receipt.png"
    object_name = f"receipts/{inv.uuid}_{filename}"
    
    # Deduce content type
    content_type = file.content_type
    
    minio_service.upload_fingerprint(file_data, object_name, content_type=content_type)
    
    # Update invoice status
    inv.payment_proof_path = object_name
    inv.status = "waiting_verification"
    
    db.commit()
    db.refresh(inv)
    
    res = InvoiceResponse.model_validate(inv)
    res.lembaga_name = inv.lembaga.name if inv.lembaga else None
    if inv.payment_proof_path:
        res.payment_proof_url = f"{str(request.base_url).rstrip('/')}/invoices/public/{inv.uuid}/proof"
            
    return res


@router.get("/public/{uuid_str}/proof")
def get_public_invoice_proof(uuid_str: str, db: Session = Depends(get_db)):
    """Fetch the payment proof file directly from MinIO and return it as a response (acts as a proxy)."""
    inv = db.query(Invoice).filter(Invoice.uuid == uuid_str).first()
    if not inv or not inv.payment_proof_path:
        raise HTTPException(status_code=404, detail="Bukti pembayaran tidak ditemukan")
        
    try:
        file_data = minio_service.get_fingerprint(inv.payment_proof_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengunduh file: {str(e)}")
        
    # Guess media type
    media_type = "image/png"
    path_lower = inv.payment_proof_path.lower()
    if path_lower.endswith(".pdf"):
        media_type = "application/pdf"
    elif path_lower.endswith(".jpg") or path_lower.endswith(".jpeg"):
        media_type = "image/jpeg"
    elif path_lower.endswith(".webp"):
        media_type = "image/webp"
    elif path_lower.endswith(".gif"):
        media_type = "image/gif"
        
    return Response(content=file_data, media_type=media_type)
