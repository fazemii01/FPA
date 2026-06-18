from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.scan import ReportResponse
from app.services.report_service import ReportService
from app.repositories.scan import ScanSessionRepository
from app.middleware.auth import get_current_user, require_permission
from app.models.user import User, UserRole
from app.models.scan_session import SessionStatus

router = APIRouter(prefix="/reports", tags=["reports"])


def _ensure_session_visible(session, user: User):
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if user.role == UserRole.SUPER_ADMIN:
        return session
    if session.lembaga_id != user.lembaga_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if user.role != UserRole.ADMIN and session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.post(
    "/sessions/{session_id}/generate",
    response_model=ReportResponse,
)
def generate_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("GENERATE_REPORT")),
):
    """Generate report for an approved session, deducting 1 credit from the institution's balance."""
    from datetime import datetime, timedelta
    from app.models.lembaga import Lembaga
    from app.models.report import Report

    session = ScanSessionRepository.get_session(db, session_id)
    _ensure_session_visible(session, current_user)
    
    if session.status == SessionStatus.GENERATING_REPORT:
        stuck_cutoff = datetime.utcnow() - timedelta(minutes=2)
        if session.updated_at and session.updated_at > stuck_cutoff:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Laporan sedang diproses. Harap tunggu beberapa saat.",
            )
    elif session.status not in (SessionStatus.APPROVED, SessionStatus.REPORT_GENERATED):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Report generation requires APPROVED status (current: {session.status.value})",
        )

    # Check if a report was already generated (regeneration does not consume additional credits)
    is_regeneration = session.status == SessionStatus.REPORT_GENERATED
    
    try:
        if not is_regeneration:
            if not session.lembaga_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sesi tidak terasosiasi dengan lembaga mana pun.",
                )
            # Lock the Lembaga row for atomic credit deduction
            lembaga = db.query(Lembaga).filter(Lembaga.id == session.lembaga_id).with_for_update().first()
            if not lembaga:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lembaga tidak ditemukan.",
                )
            if lembaga.credits <= 0:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Kredit lembaga habis. Silakan hubungi super admin untuk pengisian kredit.",
                )
            # Deduct 1 credit
            lembaga.credits -= 1
            db.flush()

        # Update status to GENERATING_REPORT
        session.status = SessionStatus.GENERATING_REPORT
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memproses transaksi kredit: {exc}",
        )

    try:
        report = ReportService.generate_report(db, session_id)
        
        # Mark as completed
        session.status = SessionStatus.REPORT_GENERATED
        session.completed_at = datetime.utcnow()
        
        # Link report to the institution
        db_report = db.query(Report).filter(Report.scan_session_id == session_id).first()
        if db_report and db_report.lembaga_id is None:
            db_report.lembaga_id = session.lembaga_id

        db.commit()
        return report
    except Exception as exc:
        db.rollback()
        # Refund credits and reset status if first-time generation fails
        try:
            session.status = SessionStatus.APPROVED
            if not is_regeneration and session.lembaga_id:
                lembaga = db.query(Lembaga).filter(Lembaga.id == session.lembaga_id).first()
                if lembaga:
                    lembaga.credits += 1
            db.commit()
        except Exception as refund_exc:
            db.rollback()
            print(f"Failed to refund credits: {refund_exc}")
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pembuatan laporan gagal: {exc}",
        ) from exc


@router.get(
    "/sessions/{session_id}",
    response_model=ReportResponse,
)
def get_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("VIEW_HISTORY")),
):
    session = ScanSessionRepository.get_session(db, session_id)
    _ensure_session_visible(session, current_user)

    report = ReportService.get_report(db, session_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report
