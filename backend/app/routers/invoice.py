from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, Response
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.database import get_db
from app.middleware.auth import require_super_admin
from app.models.invoice import Invoice
from app.models.lembaga import Lembaga
from app.models.payment_log import PaymentLog
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

@router.post("", response_model=InvoiceResponse, dependencies=[Depends(require_super_admin)])
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    """Create a new top-up invoice (Super Admin only)."""
    # Verify Lembaga exists
    lembaga = db.query(Lembaga).filter(Lembaga.id == payload.lembaga_id).first()
    if not lembaga:
        raise HTTPException(status_code=404, detail="Lembaga tidak ditemukan")
        
    # Calculate amount
    price_per_credit = 300000.0
    subtotal = payload.credits * price_per_credit
    total_amount = subtotal - payload.discount
    if total_amount < 0:
        total_amount = 0.0

    inv_code = generate_invoice_code(db)
    inv = Invoice(
        lembaga_id=payload.lembaga_id,
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
    res.lembaga_name = lembaga.name
    return res


@router.get("", response_model=List[InvoiceResponse], dependencies=[Depends(require_super_admin)])
def list_invoices(request: Request, db: Session = Depends(get_db)):
    """List all invoices for super admin dashboard."""
    invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
    result = []
    for inv in invoices:
        res = InvoiceResponse.model_validate(inv)
        res.lembaga_name = inv.lembaga.name if inv.lembaga else None
        if inv.payment_proof_path:
            res.payment_proof_url = f"{str(request.base_url).rstrip('/')}/invoices/public/{inv.uuid}/proof"
        result.append(res)
    return result


@router.delete("/{invoice_id}", dependencies=[Depends(require_super_admin)])
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Delete an invoice."""
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    
    # Delete payment proof from minio if exists
    if inv.payment_proof_path:
        try:
            minio_service.delete_fingerprint(inv.payment_proof_path)
        except Exception:
            pass
            
    db.delete(inv)
    db.commit()
    return {"status": "success"}


@router.post("/{invoice_id}/approve", response_model=InvoiceResponse, dependencies=[Depends(require_super_admin)])
def approve_invoice(invoice_id: int, request: Request, db: Session = Depends(get_db)):
    """Approve invoice payment, add credits to institution, and log the transaction."""
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).with_for_update().first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
        
    if inv.status == "success":
        raise HTTPException(status_code=400, detail="Invoice sudah lunas")
        
    lembaga = db.query(Lembaga).filter(Lembaga.id == inv.lembaga_id).with_for_update().first()
    if not lembaga:
        raise HTTPException(status_code=404, detail="Lembaga dari invoice tidak ditemukan")
        
    # Transactional update
    lembaga.credits += inv.credits
    
    # Log payment
    log = PaymentLog(
        lembaga_id=inv.lembaga_id,
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
    res.lembaga_name = lembaga.name
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
