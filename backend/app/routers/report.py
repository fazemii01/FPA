from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.scan import ReportResponse
from app.services.report_service import ReportService
from app.repositories.scan import ScanSessionRepository
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/sessions/{session_id}/generate", response_model=ReportResponse)
def generate_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = ScanSessionRepository.get_session(db, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    report = ReportService.generate_report(db, session_id)
    return report


@router.get("/sessions/{session_id}", response_model=ReportResponse)
def get_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = ScanSessionRepository.get_session(db, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    report = ReportService.get_report(db, session_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    return report
