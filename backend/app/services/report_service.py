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
        
        # Sanitize participant name to be filename-safe (spaces replaced by underscores)
        safe_name = "".join(c for c in session.participant_name if c.isalnum() or c in "._- ").strip()
        safe_name = safe_name.replace(" ", "_")
        if not safe_name:
            safe_name = "report"
            
        pdf_path = f"reports/{session.user_id}/{scan_session_id}/{safe_name}.pdf"
        minio_service.upload_fingerprint(pdf_bytes, pdf_path)
        
        from datetime import datetime

        report = db.query(Report).filter(Report.scan_session_id == scan_session_id).first()
        if report:
            report.overall_score = average_quality
            report.pdf_path = pdf_path
            report.metrics = metrics
            report.created_at = datetime.utcnow()
            if report.lembaga_id is None:
                report.lembaga_id = session.lembaga_id
        else:
            report = Report(
                scan_session_id=scan_session_id,
                lembaga_id=session.lembaga_id,
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
