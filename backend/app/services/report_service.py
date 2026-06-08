from sqlalchemy.orm import Session
from app.models.report import Report
from app.models.scan_session import ScanSession
from app.repositories.scan import FingerprintRepository, FingerprintFeatureRepository
from app.report_engine.html_generator import HTMLReportGenerator
from app.storage.minio_service import MinIOService


class ReportService:
    @staticmethod
    def generate_report(db: Session, scan_session_id: int) -> Report:
        session = db.query(ScanSession).filter(ScanSession.id == scan_session_id).first()
        if not session:
            raise Exception("Session not found")
        
        # 1. Fetch fingerprints for basic quality metrics
        fingerprints = FingerprintRepository.get_session_fingerprints(db, scan_session_id)
        quality_scores = {}
        total_quality = 0
        for fp in fingerprints:
            quality_scores[fp.finger_position.value] = fp.quality_score or 0
            total_quality += fp.quality_score or 0
        average_quality = total_quality / len(fingerprints) if fingerprints else 0
        
        metrics = {
            "total_fingerprints": len(fingerprints),
            "quality_scores": quality_scores,
            "average_quality": average_quality
        }
        
        # 2. Fetch all fingerprint features (containing pattern types & ridge counts)
        db_features = FingerprintFeatureRepository.get_session_features(db, scan_session_id)
        features_list = [
            {
                "finger_position": feat.fingerprint.finger_position.value if feat.fingerprint else "unknown",
                "pattern_type": feat.pattern_type,
                "ridge_count": feat.ridge_count
            }
            for feat in db_features
        ]
        
        # 3. Generate high-fidelity PDF from HTML + CSS
        pdf_bytes = HTMLReportGenerator.generate_pdf_report(session.participant_name, features_list)
        
        minio_service = MinIOService()
        pdf_path = f"reports/{session.user_id}/{scan_session_id}/report.pdf"
        minio_service.upload_fingerprint(pdf_bytes, pdf_path)
        
        report = Report(
            scan_session_id=scan_session_id,
            overall_score=average_quality,
            pdf_path=pdf_path,
            metrics=metrics
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        return report
    
    @staticmethod
    def get_report(db: Session, scan_session_id: int) -> Report:
        return db.query(Report).filter(Report.scan_session_id == scan_session_id).first()
