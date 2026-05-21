from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from datetime import datetime
import io


class ReportGenerator:
    @staticmethod
    def generate_pdf(scan_session_id: int, metrics: dict, fingerprints: list) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1
        )
        
        elements.append(Paragraph("Fingerprint Scan Report", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        info_data = [
            ["Scan Session ID", str(scan_session_id)],
            ["Generated Date", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")],
            ["Total Fingerprints", str(metrics.get("total_fingerprints", 0))],
            ["Average Quality Score", f"{metrics.get('average_quality', 0):.2f}%"]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        if fingerprints:
            elements.append(Paragraph("Fingerprint Details", styles['Heading2']))
            elements.append(Spacer(1, 0.2*inch))
            
            fp_data = [["Position", "Quality Score", "Status"]]
            for fp in fingerprints:
                quality = fp.get("quality_score", 0)
                status = "Good" if quality >= 70 else "Fair" if quality >= 50 else "Poor"
                fp_data.append([
                    fp.get("finger_position", "Unknown"),
                    f"{quality:.2f}%",
                    status
                ])
            
            fp_table = Table(fp_data, colWidths=[2*inch, 2*inch, 2*inch])
            fp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            elements.append(fp_table)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
