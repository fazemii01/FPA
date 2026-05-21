from sqlalchemy.orm import Session
from app.models.report import Report
from app.models.scan_session import ScanSession
from app.repositories.scan import FingerprintRepository
from app.report_engine.generator import ReportGenerator
from app.storage.minio_service import MinIOService


class ReportService:
    @staticmethod
    def generate_report(db: Session, scan_session_id: int) -> Report:
        session = db.query(ScanSession).filter(ScanSession.id == scan_session_id).first()
        if not session:
            raise Exception("Session not found")
        
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
        
        fingerprint_data = [
            {
                "finger_position": fp.finger_position.value,
                "quality_score": fp.quality_score or 0
            }
            for fp in fingerprints
        ]
        
        pdf_bytes = ReportGenerator.generate_pdf(scan_session_id, metrics, fingerprint_data)
        
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
