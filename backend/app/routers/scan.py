from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.scan import ScanSessionResponse, FingerprintResponse, FingerPositionEnum
from app.repositories.scan import ScanSessionRepository, FingerprintRepository
from app.repositories.user import UserRepository
from app.storage.minio_service import MinIOService
from app.processing.image_processor import ImageProcessingService
from app.middleware.auth import get_current_user
from app.models.user import User
import uuid

router = APIRouter(prefix="/scans", tags=["scans"])
minio_service = MinIOService()
image_processor = ImageProcessingService()


@router.post("/sessions", response_model=ScanSessionResponse)
def create_scan_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = ScanSessionRepository.create_session(db, current_user.id)
    return session


@router.get("/sessions/{session_id}", response_model=ScanSessionResponse)
def get_scan_session(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = ScanSessionRepository.get_session(db, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.get("/sessions", response_model=list[ScanSessionResponse])
def list_user_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sessions = ScanSessionRepository.get_user_sessions(db, current_user.id)
    return sessions


@router.post("/sessions/{session_id}/fingerprints", response_model=FingerprintResponse)
async def upload_fingerprint(
    session_id: int,
    finger_position: FingerPositionEnum,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = ScanSessionRepository.get_session(db, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    file_data = await file.read()
    
    quality_score = image_processor.calculate_quality_score(file_data)
    normalized_data = image_processor.normalize_fingerprint(file_data)
    
    object_name = f"fingerprints/{current_user.id}/{session_id}/{finger_position}_{uuid.uuid4()}.png"
    minio_service.upload_fingerprint(normalized_data, object_name)
    
    fingerprint = FingerprintRepository.create_fingerprint(
        db, session_id, finger_position, object_name
    )
    FingerprintRepository.update_quality_score(db, fingerprint.id, quality_score)
    
    return fingerprint


@router.get("/sessions/{session_id}/fingerprints", response_model=list[FingerprintResponse])
def get_session_fingerprints(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = ScanSessionRepository.get_session(db, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    fingerprints = FingerprintRepository.get_session_fingerprints(db, session_id)
    return fingerprints
