from typing import Optional, List
from sqlalchemy.orm import Session, joinedload, selectinload
from app.models.scan_session import ScanSession, SessionStatus
from app.models.fingerprint import Fingerprint, FingerPosition
from app.models.fingerprint_feature import FingerprintFeature
from app.models.report import Report
from app.schemas.scan import ScanSessionCreate
from datetime import datetime


class ScanSessionRepository:
    @staticmethod
    def create_session(db: Session, user_id: int, payload: ScanSessionCreate) -> ScanSession:
        from app.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        lembaga_id = user.lembaga_id if user else None

        session = ScanSession(
            user_id=user_id,
            lembaga_id=lembaga_id,
            participant_name=payload.participant_name,
            participant_age=payload.participant_age,
            participant_gender=payload.participant_gender,
            notes=payload.notes,
            status=SessionStatus.REGISTERED,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(db: Session, session_id: int) -> Optional[ScanSession]:
        return (
            db.query(ScanSession)
            .options(
                selectinload(ScanSession.fingerprints).joinedload(Fingerprint.features),
                joinedload(ScanSession.user)
            )
            .filter(ScanSession.id == session_id)
            .first()
        )

    @staticmethod
    def get_user_sessions(db: Session, user_id: int) -> List[ScanSession]:
        return (
            db.query(ScanSession)
            .options(
                selectinload(ScanSession.fingerprints).joinedload(Fingerprint.features),
                joinedload(ScanSession.user)
            )
            .filter(ScanSession.user_id == user_id)
            .order_by(ScanSession.created_at.desc())
            .all()
        )

    @staticmethod
    def get_user_sessions_by_lembaga(db: Session, user_id: int, lembaga_id: int) -> List[ScanSession]:
        return (
            db.query(ScanSession)
            .options(
                selectinload(ScanSession.fingerprints).joinedload(Fingerprint.features),
                joinedload(ScanSession.user)
            )
            .filter(ScanSession.user_id == user_id, ScanSession.lembaga_id == lembaga_id)
            .order_by(ScanSession.created_at.desc())
            .all()
        )

    @staticmethod
    def get_all_sessions(db: Session, status: Optional[SessionStatus] = None) -> List[ScanSession]:
        q = db.query(ScanSession).options(
            selectinload(ScanSession.fingerprints).joinedload(Fingerprint.features),
            joinedload(ScanSession.user)
        )
        if status is not None:
            q = q.filter(ScanSession.status == status)
        return q.order_by(ScanSession.created_at.desc()).all()

    @staticmethod
    def get_all_sessions_by_lembaga(
        db: Session, lembaga_id: int, status: Optional[SessionStatus] = None
    ) -> List[ScanSession]:
        q = db.query(ScanSession).options(
            selectinload(ScanSession.fingerprints).joinedload(Fingerprint.features),
            joinedload(ScanSession.user)
        ).filter(ScanSession.lembaga_id == lembaga_id)
        if status is not None:
            q = q.filter(ScanSession.status == status)
        return q.order_by(ScanSession.created_at.desc()).all()

    @staticmethod
    def update_session_status(
        db: Session,
        session_id: int,
        status: SessionStatus,
    ) -> Optional[ScanSession]:
        session = ScanSessionRepository.get_session(db, session_id)
        if not session:
            return None
        session.status = status
        now = datetime.utcnow()
        if status == SessionStatus.WAITING_FOR_REVIEW and session.submitted_at is None:
            session.submitted_at = now
        if status == SessionStatus.APPROVED and session.approved_at is None:
            session.approved_at = now
        if status == SessionStatus.NEED_RESCAN and session.reviewed_at is None:
            session.reviewed_at = now
        if status in (SessionStatus.REPORT_GENERATED, SessionStatus.REJECTED) and session.completed_at is None:
            session.completed_at = now
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def mark_reviewed(
        db: Session,
        session_id: int,
        reviewer_id: int,
        decision: SessionStatus,
        rejection_reason: Optional[str] = None,
    ) -> Optional[ScanSession]:
        session = ScanSessionRepository.get_session(db, session_id)
        if not session:
            return None
        session.reviewed_by_id = reviewer_id
        session.reviewed_at = datetime.utcnow()
        session.status = decision
        if decision == SessionStatus.REJECTED:
            session.rejection_reason = rejection_reason
        if decision == SessionStatus.APPROVED:
            session.approved_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def delete_session(db: Session, session_id: int) -> bool:
        session = ScanSessionRepository.get_session(db, session_id)
        if not session:
            return False

        # 1. Delete associated report first (has NOT NULL FK → scan_session_id)
        db.query(Report).filter(Report.scan_session_id == session_id).delete(synchronize_session=False)
        # 2. Delete fingerprint features
        db.query(FingerprintFeature).filter(FingerprintFeature.scan_session_id == session_id).delete(synchronize_session=False)
        # 3. Delete fingerprints
        db.query(Fingerprint).filter(Fingerprint.scan_session_id == session_id).delete(synchronize_session=False)
        # 4. Delete the session itself
        db.delete(session)
        db.commit()
        return True


class FingerprintRepository:
    @staticmethod
    def create_fingerprint(
        db: Session,
        scan_session_id: int,
        finger_position: FingerPosition,
        image_path: str,
    ) -> Fingerprint:
        fingerprint = Fingerprint(
            scan_session_id=scan_session_id,
            finger_position=finger_position,
            image_path=image_path,
        )
        db.add(fingerprint)
        db.commit()
        db.refresh(fingerprint)
        return fingerprint

    @staticmethod
    def get_fingerprint(db: Session, fingerprint_id: int) -> Optional[Fingerprint]:
        return (
            db.query(Fingerprint)
            .options(joinedload(Fingerprint.features))
            .filter(Fingerprint.id == fingerprint_id)
            .first()
        )

    @staticmethod
    def get_session_fingerprints(db: Session, session_id: int) -> List[Fingerprint]:
        return (
            db.query(Fingerprint)
            .options(joinedload(Fingerprint.features))
            .filter(Fingerprint.scan_session_id == session_id)
            .all()
        )

    @staticmethod
    def update_quality_score(db: Session, fingerprint_id: int, quality_score: float) -> Optional[Fingerprint]:
        fingerprint = FingerprintRepository.get_fingerprint(db, fingerprint_id)
        if fingerprint:
            fingerprint.quality_score = float(quality_score) if quality_score is not None else None
            db.commit()
            db.refresh(fingerprint)
        return fingerprint

    @staticmethod
    def delete_by_position(db: Session, session_id: int, position: FingerPosition) -> int:
        fps_to_delete = (
            db.query(Fingerprint)
            .filter(
                Fingerprint.scan_session_id == session_id,
                Fingerprint.finger_position == position,
            )
            .all()
        )
        if fps_to_delete:
            fp_ids = [fp.id for fp in fps_to_delete]
            # Delete associated features first to avoid foreign key violations
            db.query(FingerprintFeature).filter(FingerprintFeature.fingerprint_id.in_(fp_ids)).delete(synchronize_session=False)
            
            deleted = (
                db.query(Fingerprint)
                .filter(Fingerprint.id.in_(fp_ids))
                .delete(synchronize_session=False)
            )
            db.commit()
            return int(deleted)
        return 0


class FingerprintFeatureRepository:
    @staticmethod
    def upsert_features(
        db: Session,
        fingerprint_id: int,
        scan_session_id: int,
        features: dict,
    ) -> FingerprintFeature:
        row = (
            db.query(FingerprintFeature)
            .filter(FingerprintFeature.fingerprint_id == fingerprint_id)
            .first()
        )
        if row is None:
            row = FingerprintFeature(
                fingerprint_id=fingerprint_id,
                scan_session_id=scan_session_id,
            )
            db.add(row)
        row.pattern_type = str(features.get("pattern_type") or "unknown")
        row.ridge_count = int(features.get("ridge_count") or 0)
        row.ridge_density = float(features.get("ridge_density") or 0.0)
        row.orientation_stability = float(features.get("orientation_stability") or 0.0)
        row.minutiae_count = len(features.get("minutiae") or [])
        row.core_count = len(features.get("core_points") or [])
        row.delta_count = len(features.get("delta_points") or [])
        row.quality_score = float(features.get("quality_score") or 0.0)
        row.features_json = features
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def get_session_features(db: Session, session_id: int) -> List[FingerprintFeature]:
        return (
            db.query(FingerprintFeature)
            .options(joinedload(FingerprintFeature.fingerprint))
            .filter(FingerprintFeature.scan_session_id == session_id)
            .all()
        )

    @staticmethod
    def update_features(
        db: Session,
        fingerprint_id: int,
        pattern_type: str,
        ridge_count: int,
    ) -> Optional[FingerprintFeature]:
        row = (
            db.query(FingerprintFeature)
            .filter(FingerprintFeature.fingerprint_id == fingerprint_id)
            .first()
        )
        if row is None:
            return None
        row.pattern_type = pattern_type
        row.ridge_count = ridge_count
        
        if row.features_json:
            features = dict(row.features_json)
            features["pattern_type"] = pattern_type
            features["ridge_count"] = ridge_count
            row.features_json = features
            
        db.commit()
        db.refresh(row)
        return row
