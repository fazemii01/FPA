from sqlalchemy.orm import Session
from app.models.scan_session import ScanSession, SessionStatus
from app.models.fingerprint import Fingerprint, FingerPosition
from datetime import datetime


class ScanSessionRepository:
    @staticmethod
    def create_session(db: Session, user_id: int) -> ScanSession:
        session = ScanSession(user_id=user_id, status=SessionStatus.IN_PROGRESS)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_session(db: Session, session_id: int) -> ScanSession:
        return db.query(ScanSession).filter(ScanSession.id == session_id).first()
    
    @staticmethod
    def get_user_sessions(db: Session, user_id: int):
        return db.query(ScanSession).filter(ScanSession.user_id == user_id).all()
    
    @staticmethod
    def update_session_status(db: Session, session_id: int, status: SessionStatus) -> ScanSession:
        session = ScanSessionRepository.get_session(db, session_id)
        if session:
            session.status = status
            if status == SessionStatus.COMPLETED:
                session.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session


class FingerprintRepository:
    @staticmethod
    def create_fingerprint(db: Session, scan_session_id: int, finger_position: FingerPosition, image_path: str) -> Fingerprint:
        fingerprint = Fingerprint(
            scan_session_id=scan_session_id,
            finger_position=finger_position,
            image_path=image_path
        )
        db.add(fingerprint)
        db.commit()
        db.refresh(fingerprint)
        return fingerprint
    
    @staticmethod
    def get_fingerprint(db: Session, fingerprint_id: int) -> Fingerprint:
        return db.query(Fingerprint).filter(Fingerprint.id == fingerprint_id).first()
    
    @staticmethod
    def get_session_fingerprints(db: Session, session_id: int):
        return db.query(Fingerprint).filter(Fingerprint.scan_session_id == session_id).all()
    
    @staticmethod
    def update_quality_score(db: Session, fingerprint_id: int, quality_score: float) -> Fingerprint:
        fingerprint = FingerprintRepository.get_fingerprint(db, fingerprint_id)
        if fingerprint:
            fingerprint.quality_score = float(quality_score) if quality_score is not None else None
            db.commit()
            db.refresh(fingerprint)
        return fingerprint
