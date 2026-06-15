from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import uuid
import io

from app.db.database import get_db
from app.schemas.scan import (
    ScanSessionCreate,
    ScanSessionResponse,
    FingerprintResponse,
    FingerPositionEnum,
    SessionRejectRequest,
    SessionRescanRequest,
    FingerprintFeaturesUpdate,
)
from app.repositories.scan import (
    ScanSessionRepository,
    FingerprintRepository,
    FingerprintFeatureRepository,
)
from app.storage.minio_service import MinIOService
from app.processing.image_processor import ImageProcessingService
from app.middleware.auth import (
    get_current_user,
    require_admin,
    require_staff_or_admin,
)
from app.models.user import User, UserRole
from app.models.scan_session import SessionStatus
from app.models.fingerprint import FingerPosition

router = APIRouter(prefix="/scans", tags=["scans"])
minio_service = MinIOService()
image_processor = ImageProcessingService()


def _ensure_session_visible(session, user: User):
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if user.role != UserRole.ADMIN and session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.post(
    "/sessions",
    response_model=ScanSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_scan_session(
    payload: ScanSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
):
    return ScanSessionRepository.create_session(db, current_user.id, payload)


@router.get("/sessions/{session_id}", response_model=ScanSessionResponse)
def get_scan_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = ScanSessionRepository.get_session(db, session_id)
    return _ensure_session_visible(session, current_user)


@router.get("/sessions", response_model=list[ScanSessionResponse])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.ADMIN:
        return ScanSessionRepository.get_all_sessions(db)
    return ScanSessionRepository.get_user_sessions(db, current_user.id)


@router.get(
    "/review-queue",
    response_model=list[ScanSessionResponse],
)
def list_review_queue(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return ScanSessionRepository.get_all_sessions(db, status=SessionStatus.WAITING_FOR_REVIEW)


@router.post(
    "/sessions/{session_id}/fingerprints",
    response_model=FingerprintResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_fingerprint(
    session_id: int,
    finger_position: FingerPositionEnum,
    file: UploadFile = File(...),
    enhanced_file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
):
    session = ScanSessionRepository.get_session(db, session_id)
    _ensure_session_visible(session, current_user)

    if session.status not in (
        SessionStatus.DRAFT,
        SessionStatus.REGISTERED,
        SessionStatus.SCANNING,
        SessionStatus.NEED_RESCAN,
        SessionStatus.SCAN_COMPLETED,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot upload while session status is {session.status.value}",
        )

    # Replace any existing capture for this finger position
    FingerprintRepository.delete_by_position(db, session_id, FingerPosition(finger_position.value))

    file_data = await file.read()

    processing_result = image_processor.process_fingerprint(file_data)
    quality_score = processing_result["quality_score"]

    # Bypass quality threshold validation to allow continuous scanning workflow
    # if quality_score < 70.0:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail={
    #             "message": processing_result.get("reject_reason", "Kualitas sidik jari terlalu rendah."),
    #             "debug_images": processing_result.get("debug_images", {})
    #         }
    #     )

    features = processing_result["features"]
    
    if enhanced_file:
        normalized_data = await enhanced_file.read()
    else:
        normalized_data = image_processor.normalize_fingerprint(file_data)

    object_name = (
        f"fingerprints/{current_user.id}/{session_id}/"
        f"{finger_position.value}_{uuid.uuid4()}.png"
    )
    minio_service.upload_fingerprint(normalized_data, object_name)

    fingerprint = FingerprintRepository.create_fingerprint(
        db, session_id, FingerPosition(finger_position.value), object_name
    )
    FingerprintRepository.update_quality_score(db, fingerprint.id, quality_score)
    FingerprintFeatureRepository.upsert_features(db, fingerprint.id, session_id, features)

    capture_count = len(FingerprintRepository.get_session_fingerprints(db, session_id))
    if capture_count >= 10:
        ScanSessionRepository.update_session_status(db, session_id, SessionStatus.SCAN_COMPLETED)
    elif session.status in (SessionStatus.DRAFT, SessionStatus.REGISTERED, SessionStatus.NEED_RESCAN):
        ScanSessionRepository.update_session_status(db, session_id, SessionStatus.SCANNING)

    db.refresh(fingerprint)
    return fingerprint


@router.get(
    "/sessions/{session_id}/fingerprints",
    response_model=list[FingerprintResponse],
)
def get_session_fingerprints(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = ScanSessionRepository.get_session(db, session_id)
    _ensure_session_visible(session, current_user)
    return FingerprintRepository.get_session_fingerprints(db, session_id)


@router.get("/fingerprints/{fingerprint_id}/image")
def get_fingerprint_image(
    fingerprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Proxy endpoint: fetches the fingerprint image from MinIO and streams it back."""
    fingerprint = FingerprintRepository.get_fingerprint(db, fingerprint_id)
    if fingerprint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fingerprint not found")

    # Verify the requesting user can access the parent session
    session = ScanSessionRepository.get_session(db, fingerprint.scan_session_id)
    _ensure_session_visible(session, current_user)

    try:
        image_bytes = minio_service.get_fingerprint(fingerprint.image_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image not found in storage: {e}",
        )

    return StreamingResponse(
        io.BytesIO(image_bytes),
        media_type="image/png",
        headers={"Cache-Control": "private, max-age=3600"},
    )


@router.post("/sessions/{session_id}/submit", response_model=ScanSessionResponse)
def submit_for_review(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
):
    session = ScanSessionRepository.get_session(db, session_id)
    _ensure_session_visible(session, current_user)

    fps = FingerprintRepository.get_session_fingerprints(db, session_id)
    if len(fps) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Need 10 fingerprints to submit (currently {len(fps)})",
        )

    if session.status not in (
        SessionStatus.SCANNING,
        SessionStatus.SCAN_COMPLETED,
        SessionStatus.NEED_RESCAN,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot submit while status is {session.status.value}",
        )

    return ScanSessionRepository.update_session_status(
        db, session_id, SessionStatus.WAITING_FOR_REVIEW
    )


@router.post("/sessions/{session_id}/approve", response_model=ScanSessionResponse)
def approve_session(
    session_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    session = ScanSessionRepository.get_session(db, session_id)
    _ensure_session_visible(session, admin)
    if session.status != SessionStatus.WAITING_FOR_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only sessions in WAITING_FOR_REVIEW can be approved (current: {session.status.value})",
        )
    return ScanSessionRepository.mark_reviewed(db, session_id, admin.id, SessionStatus.APPROVED)


@router.post("/sessions/{session_id}/reject", response_model=ScanSessionResponse)
def reject_session(
    session_id: int,
    payload: SessionRejectRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    session = ScanSessionRepository.get_session(db, session_id)
    _ensure_session_visible(session, admin)
    if session.status != SessionStatus.WAITING_FOR_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only sessions in WAITING_FOR_REVIEW can be rejected (current: {session.status.value})",
        )
    return ScanSessionRepository.mark_reviewed(
        db, session_id, admin.id, SessionStatus.REJECTED, rejection_reason=payload.reason
    )


@router.post("/sessions/{session_id}/request-rescan", response_model=ScanSessionResponse)
def request_rescan(
    session_id: int,
    payload: SessionRescanRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    session = ScanSessionRepository.get_session(db, session_id)
    _ensure_session_visible(session, admin)
    if session.status != SessionStatus.WAITING_FOR_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only sessions in WAITING_FOR_REVIEW can be sent back for rescan (current: {session.status.value})",
        )
    for pos in payload.finger_positions:
        FingerprintRepository.delete_by_position(db, session_id, FingerPosition(pos.value))
    session.reviewed_by_id = admin.id
    session.rejection_reason = payload.reason
    return ScanSessionRepository.update_session_status(db, session_id, SessionStatus.NEED_RESCAN)


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_scan_session(
    session_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    success = ScanSessionRepository.delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/fingerprints/{fingerprint_id}/features",
    response_model=FingerprintResponse,
)
def update_fingerprint_features(
    fingerprint_id: int,
    payload: FingerprintFeaturesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
):
    fingerprint = FingerprintRepository.get_fingerprint(db, fingerprint_id)
    if fingerprint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fingerprint not found")

    session = ScanSessionRepository.get_session(db, fingerprint.scan_session_id)
    _ensure_session_visible(session, current_user)

    if session.status not in (
        SessionStatus.DRAFT,
        SessionStatus.REGISTERED,
        SessionStatus.SCANNING,
        SessionStatus.SCAN_COMPLETED,
        SessionStatus.WAITING_FOR_REVIEW,
        SessionStatus.NEED_RESCAN,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot edit features when session status is {session.status.value}",
        )

    res = FingerprintFeatureRepository.update_features(
        db, fingerprint_id, payload.pattern_type, payload.ridge_count
    )
    if res is None:
        # Fallback if no feature record exists
        FingerprintFeatureRepository.upsert_features(
            db, fingerprint_id, session.id, {
                "pattern_type": payload.pattern_type,
                "ridge_count": payload.ridge_count
            }
        )

    db.refresh(fingerprint)
    return fingerprint
