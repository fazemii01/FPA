from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.scan import ReportResponse
from app.services.report_service import ReportService
from app.repositories.scan import ScanSessionRepository
from app.middleware.auth import get_current_user, require_admin
from app.models.user import User, UserRole
from app.models.scan_session import SessionStatus

router = APIRouter(prefix="/reports", tags=["reports"])


def _ensure_session_visible(session, user: User):
    if session is None:
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
    admin: User = Depends(require_admin),
):
    """Admin-only: Generate report for an approved session."""
    session = ScanSessionRepository.get_session(db, session_id)
    _ensure_session_visible(session, admin)
    if session.status != SessionStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Report generation requires APPROVED status (current: {session.status.value})",
        )

    ScanSessionRepository.update_session_status(db, session_id, SessionStatus.GENERATING_REPORT)
    try:
        report = ReportService.generate_report(db, session_id)
        ScanSessionRepository.update_session_status(db, session_id, SessionStatus.REPORT_GENERATED)
        return report
    except Exception as exc:
        # Roll back to APPROVED so it can be retried
        ScanSessionRepository.update_session_status(db, session_id, SessionStatus.APPROVED)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {exc}",
        ) from exc


@router.get(
    "/sessions/{session_id}",
    response_model=ReportResponse,
)
def get_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = ScanSessionRepository.get_session(db, session_id)
    _ensure_session_visible(session, current_user)

    report = ReportService.get_report(db, session_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report
