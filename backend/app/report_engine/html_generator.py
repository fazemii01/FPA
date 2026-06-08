import os
import io
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

try:
    import weasyprint
except ImportError:
    weasyprint = None

try:
    from xhtml2pdf import pisa
except ImportError:
    pisa = None

# Custom CSS for WeasyPrint to handle page-breaks and print layout
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Advance Report - {participant_name}</title>
    <style>
        /* xhtml2pdf strict layout: NO flexbox, NO grid, NO inline-block, NO border-radius */
        
        @page {{
            size: A4;
            margin: 5mm;
        }}
        
        body {{
            font-family: Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #333333;
            background-color: #ffffff;
            -pdf-keep-with-next: true;
        }}
        
        .page {{
            width: 196mm;
            page-break-after: always;
            position: relative;
            background-color: #ffffff;
            border: 6px solid #1B365D;
        }}
        
        .page-inner {{
            border: 2px solid #F15A24;
            margin: 4px;
            padding: 24px 34px;
        }}
        
        .page:last-child {{
            page-break-after: avoid;
        }}
        
        /* Cover Page styling */
        .cover {{
            text-align: center;
            padding: 10px 15px;
        }}
        
        .cover-title {{
            font-size: 24pt;
            font-weight: 500;
            letter-spacing: 4px;
            color: #555555;
            margin-bottom: 5px;
        }}
        
        .cover-subtitle {{
            font-size: 34pt;
            font-weight: 800;
            color: #1B365D;
            margin: 10px 0;
            line-height: 1.2;
        }}
        
        .cover-badge {{
            font-size: 20pt;
            font-weight: 700;
            color: #F15A24;
            letter-spacing: 2px;
            border-bottom: 2px solid #F15A24;
            padding-bottom: 8px;
            margin-bottom: 40px;
        }}
        
        .cover-fingerprint {{
            width: 200px;
            height: 200px;
            margin: 30px auto;
            opacity: 0.15;
        }}
        
        .cover-logo {{
            font-size: 28pt;
            font-weight: 800;
            color: #F15A24;
            margin-bottom: 0;
        }}
        .cover-logo span {{
            color: #1B365D;
        }}
        
        .cover-box {{
            margin: 50px auto 0 auto;
            width: 80%;
            background-color: #F4F6F9;
            border: 1px solid #e1e7e5;
            padding: 20px;
        }}
        
        .cover-name-label {{
            font-size: 11pt;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }}
        
        .cover-name {{
            font-size: 22pt;
            font-weight: 700;
            color: #1B365D;
        }}
        
        /* Headers and Typography */
        .section-header {{
            background-color: #1B365D;
            color: white;
            padding: 10px 20px;
            font-size: 14pt;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 25px;
            text-align: center;
        }}
        
        .participant-highlight {{
            text-align: center;
            font-size: 13pt;
            margin-bottom: 20px;
            color: #555;
            background: transparent;
            border: none;
        }}
        .participant-highlight span {{
            color: #1B365D;
            font-weight: 700;
            border-bottom: 1.5px solid #1B365D;
        }}
        
        /* Table / Rows styling - NO flex, pure block */
        .data-row {{
            margin-bottom: 12px;
            background: #fdfdfd;
            border: 1px solid #e9eff4;
            padding: 8px 15px;
        }}
        
        .data-val {{
            width: 75px;
            font-size: 14pt;
            font-weight: 800;
            color: #1B365D;
        }}
        
        .data-label {{
            width: 140px;
            font-size: 11pt;
            font-weight: 700;
            color: #fff;
            background-color: #1B365D;
            padding: 5px 10px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-right: 15px;
        }}
        
        .data-label.orange {{
            background-color: #F15A24;
        }}
        
        .data-desc {{
            font-size: 9pt;
            line-height: 1.4;
            color: #555;
        }}
        
        /* Progress bars - no flex, use table for layout */
        .progress-container {{
            margin-bottom: 18px;
            background: #fafbfc;
            border: 1px solid #eaeaea;
            padding: 12px;
        }}
        .progress-label {{
            width: 150px;
            font-size: 11pt;
            font-weight: 600;
            color: #333;
        }}
        .progress-bar-bg {{
            height: 12px;
            background-color: #eef2f3;
            overflow: hidden;
            margin: 0 15px;
        }}
        .progress-bar-fill {{
            height: 100%;
            background-color: #1B365D;
        }}
        .progress-bar-fill.orange {{
            background-color: #F15A24;
        }}
        .progress-val {{
            width: 55px;
            font-size: 12pt;
            font-weight: 700;
            color: #1B365D;
            text-align: right;
        }}
        
        /* Grid layout - replaced with table */
        .grid-col {{
            background: #fafbfc;
            border: 1px solid #eef2f5;
            padding: 20px;
        }}
        
        .grid-col-header {{
            font-size: 12pt;
            font-weight: 700;
            color: #1B365D;
            border-bottom: 2px solid #1B365D;
            padding-bottom: 8px;
            margin-bottom: 12px;
            text-transform: uppercase;
            text-align: center;
        }}
        
        .badge {{
            padding: 8px 16px;
            background-color: #f1f4f9;
            border: 1.5px solid #1B365D;
            color: #1B365D;
            font-size: 12pt;
            font-weight: 700;
            text-align: center;
            min-width: 100px;
        }}
        .badge.orange {{
            border-color: #F15A24;
            color: #F15A24;
            background-color: #fdf5f1;
        }}
        
        /* Lists & Tables */
        .rec-table {{
            width: 100%;
            table-layout: fixed;
            border-collapse: separate;
            border-spacing: 5px;
            margin-top: 5px;
        }}
        
        .rec-table td {{
            padding: 6px 10px;
            font-size: 9pt;
            font-weight: 500;
            border: 1px solid #ccc;
            text-align: left;
        }}
        .rec-table td.green {{
            background-color: #eafbe7;
            border-color: #b2ebb4;
            color: #2b702d;
        }}
        .rec-table td.orange {{
            background-color: #fff9e6;
            border-color: #ffe0b2;
            color: #b7791f;
        }}
        .rec-table td.red {{
            background-color: #ffebee;
            border-color: #ffcdd2;
            color: #c62828;
        }}
        
        /* Stimulation Tips Row styles */
        .tip-row {{
            display: block;
            margin-bottom: 4px;
            background: #fafbfc;
            border-left: 3px solid #1B365D;
            padding: 4px 8px;
        }}
        .tip-row.orange {{
            border-left-color: #F15A24;
        }}
        .tip-label {{
            font-size: 8.5pt;
            font-weight: bold;
            color: #1B365D;
            margin-bottom: 1px;
            text-transform: uppercase;
        }}
        .tip-label.orange {{
            color: #F15A24;
        }}
        .tip-text {{
            font-size: 8pt;
            line-height: 1.3;
            color: #444;
        }}
        
        .interpret-box {{
            background-color: #F4F6F9;
            border-left: 5px solid #1B365D;
            padding: 10px 12px;
            font-size: 9pt;
            line-height: 1.4;
            color: #444;
            margin-top: 15px;
        }}
        
        /* Footer - use table instead of flex */
        .page-footer {{
            position: absolute;
            bottom: 12px;
            left: 20px;
            right: 20px;
            font-size: 8.5pt;
            color: #888888;
        }}
    </style>
</head>
<body>

    <!-- Page 1: COVER -->
    <div class="page">
        <div class="page-inner" style="padding: 12px 20px;">
            <div class="cover">
                <div style="font-size: 18pt; font-weight: 500; letter-spacing: 4px; color: #1B365D; margin-top: 5px; text-transform: uppercase;">TES PEMETAAN</div>
                <div style="font-size: 28pt; font-weight: 800; color: #1B365D; margin: 1px 0 1px 0; letter-spacing: 1px; text-transform: uppercase;">POTENSI KECERDASAN</div>
                <div style="font-size: 12pt; font-weight: 600; color: #1B365D; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 3px;">— BERBASIS SIDIK JARI —</div>
                
                <div style="text-align: center; margin: 2px 0;">
                    <span style="color: #F15A24; font-size: 14pt;">●</span>
                </div>
                
                <div style="font-size: 22pt; font-weight: 800; color: #F15A24; letter-spacing: 3px; margin: 4px 0 6px 0; text-transform: uppercase;">ADVANCE REPORT</div>
                
                <!-- Fingerprint placeholder -->
                <div style="margin: 4px auto; width: 80px; height: 80px; text-align: center;">
                    <svg width="80" height="80" viewBox="0 0 100 100" style="opacity: 0.85;">
                        <path d="M50 10 A40 40 0 0 1 90 50 A40 40 0 0 1 50 90 A40 40 0 0 1 10 50 A40 40 0 0 1 50 10" fill="none" stroke="#1B365D" stroke-width="1.5" stroke-dasharray="3,3"/>
                        <path d="M50 20 A30 30 0 0 1 80 50 A30 30 0 0 1 50 80 A30 30 0 0 1 20 50 A30 30 0 0 1 50 20" fill="none" stroke="#F15A24" stroke-width="1.5"/>
                        <path d="M50 30 A20 20 0 0 1 70 50 A20 20 0 0 1 50 70 A20 20 0 0 1 30 50 A20 20 0 0 1 50 30" fill="none" stroke="#1B365D" stroke-width="2"/>
                        <path d="M50 40 A10 10 0 0 1 60 50 A10 10 0 0 1 50 60 A10 10 0 0 1 40 50 A10 10 0 0 1 50 40" fill="none" stroke="#F15A24" stroke-width="2"/>
                    </svg>
                </div>
                
                <!-- Logo -->
                <div style="font-size: 26pt; font-weight: 800; color: #F15A24; margin: 3px 0 0 0;">TAB <span style="color: #1B365D;">FINGER</span></div>
                <div style="font-size: 9pt; color: #666; letter-spacing: 1px; margin-bottom: 6px;">Personal Intelligence Mapping</div>
                
                <!-- Name Box -->
                <table width="90%" align="center" style="table-layout: fixed; border: 1.5px solid #1B365D; background-color: #F8F9FA; margin-bottom: 6px;">
                    <tr>
                        <td style="padding: 8px; text-align: center;">
                            <div style="font-size: 8pt; color: #666; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 5px;">NAMA PESERTA</div>
                            <div style="font-size: 20pt; font-weight: bold; color: #1B365D;">{participant_name}</div>
                        </td>
                    </tr>
                </table>
                
                <!-- Footer Info -->
                <table width="90%" align="center" style="table-layout: fixed; border: 1px solid #ddd; background-color: #FCFDFE; margin-top: 4px;">
                    <tr>
                        <td width="40" style="padding: 5px; text-align: center; vertical-align: middle;">
                            <span style="font-size: 20pt; color: #F15A24;">🛈</span>
                        </td>
                        <td style="padding: 5px 8px; font-size: 7.5pt; line-height: 1.3; color: #666; text-align: left;">
                            <strong>CATATAN:</strong> Laporan ini bersifat indikatif dan digunakan sebagai alat bantu untuk memahami potensi individu, bukan diagnosis medis.
                        </td>
                    </tr>
                </table>
            </div>
        </div>
    </div>

    <!-- Page 2: MULTIPLE INTELLIGENCE -->
    <div class="page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Multiple Intelligence / Kecerdasan Majemuk</td>
            </tr></table>
            <div class="participant-highlight">Hasil Pemetaan Potensi Kecerdasan: <span>{participant_name}</span></div>
            
            {intelligence_rows}
            
            <table width="100%" style="table-layout: fixed; margin-top: 10px;"><tr>
                <td bgcolor="#F4F6F9" style="padding: 10px 12px; font-size: 9pt; line-height: 1.4; color: #444; border-left: 4px solid #1B365D;"><strong>Analisis Singkat:</strong><br>
                Kecerdasan Anda berkembang dengan karakteristik yang unik. Kekuatan utama terletak pada kecerdasan <strong>{top_intelligence_1}</strong> dan <strong>{top_intelligence_2}</strong> yang sangat menonjol. Pendampingan yang konsisten dan bimbingan yang terarah akan membantu Anda memaksimalkan seluruh potensi ini untuk pencapaian akademis dan karir yang lebih baik.</td>
            </tr></table>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">CLICK FINGER CONSULTING</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 2</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 3: TIPS STIMULASI KECERDASAN -->
    <div class="page">
        <div class="page-inner" style="padding: 20px 35px;">
            <table width="100%" style="table-layout: fixed; margin-bottom: 8px;"><tr>
                <td bgcolor="#1B365D" style="padding: 6px 12px; color: #FFFFFF; font-size: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Tips Stimulasi Kecerdasan Genetik Majemuk</td>
            </tr></table>
            <div class="participant-highlight" style="margin-bottom: 8px; font-size: 11pt;">Saran Pengembangan Potensi: <span>{participant_name}</span></div>
            
            <div style="margin-top: 0px; margin-bottom: 0px;">
                {stimulation_tips_html}
            </div>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">CLICK FINGER CONSULTING</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 3</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 4: BRAIN DOMINANCE & PERSONALITY TYPE (DISC) -->
    <div class="page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Brain Dominance & Personality Type</td>
            </tr></table>
            <div class="participant-highlight">Pola Otak & Kepribadian: <span>{participant_name}</span></div>
            
            <!-- Brain Dominance Section -->
            <div style="margin-bottom: 12px;">
                <table width="100%" style="table-layout: fixed; margin-bottom: 8px;"><tr>
                    <td bgcolor="#F4F6F9" style="padding: 5px 10px; font-size: 10pt; font-weight: bold; color: #1B365D; text-transform: uppercase; border-left: 4px solid #F15A24;">1. Dominasi Otak</td>
                </tr></table>
                <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border: 1px solid #1B365D; margin-bottom: 6px;">
                    <tr>
                        <td width="{left_brain_pct}%" bgcolor="#1B365D" align="center" style="color: white; padding: 8px 4px; font-size: 9pt; font-weight: bold; line-height: 14px;">OTAK KIRI {left_brain_pct}%</td>
                        <td width="{right_brain_pct}%" bgcolor="#F15A24" align="center" style="color: white; padding: 8px 4px; font-size: 9pt; font-weight: bold; line-height: 14px;">OTAK KANAN {right_brain_pct}%</td>
                    </tr>
                </table>
                <div style="font-size: 8.5pt; line-height: 1.35; color: #555; background-color: #fcfdfe; border: 1px solid #eef2f5; padding: 8px;">
                    <strong>Dominasi Otak {dominant_brain}:</strong> {brain_dominance_desc}
                </div>
            </div>
            
            <!-- DISC Section -->
            <div style="margin-top: 5px;">
                <table width="100%" style="table-layout: fixed; margin-bottom: 8px;"><tr>
                    <td bgcolor="#F4F6F9" style="padding: 5px 10px; font-size: 10pt; font-weight: bold; color: #1B365D; text-transform: uppercase; border-left: 4px solid #F15A24;">2. Tipe Kepribadian DISC</td>
                </tr></table>
                
                <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-top: 5px; margin-bottom: 5px;">
                    <tr>
                        <td width="30%" style="text-align: center; vertical-align: middle;">
                            <svg width="85" height="85" viewBox="0 0 100 100">
                                <circle cx="50" cy="50" r="45" fill="#f8f9fa" stroke="#ddd" stroke-width="1"/>
                                <path d="M50 50 L50 5 A45 45 0 0 1 95 50 Z" fill="#e53935" opacity="0.85"/>
                                <path d="M50 50 L95 50 A45 45 0 0 1 50 95 Z" fill="#ffb300" opacity="0.85"/>
                                <path d="M50 50 L50 95 A45 45 0 0 1 5 50 Z" fill="#1e88e5" opacity="0.85"/>
                                <path d="M50 50 L5 50 A45 45 0 0 1 50 5 Z" fill="#43a047" opacity="0.85"/>
                                <text x="26" y="32" font-family="Outfit" font-size="10" font-weight="bold" fill="white">D</text>
                                <text x="70" y="32" font-family="Outfit" font-size="10" font-weight="bold" fill="white">I</text>
                                <text x="70" y="72" font-family="Outfit" font-size="10" font-weight="bold" fill="white">S</text>
                                <text x="26" y="72" font-family="Outfit" font-size="10" font-weight="bold" fill="white">C</text>
                            </svg>
                        </td>
                        <td width="70%" style="vertical-align: middle; text-align: center;">
                            <table style="table-layout: fixed; margin: 0 auto; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 0 10px; text-align: center;">
                                        <div style="font-size: 8pt; color: #666; margin-bottom: 3px;">PRIMARY</div>
                                        <table style="table-layout: fixed; margin: 0 auto;"><tr>
                                            <td bgcolor="#1B365D" align="center" style="color: white; padding: 5px 10px; font-size: 10pt; font-weight: bold; min-width: 80px;">{disc_primary}</td>
                                        </tr></table>
                                    </td>
                                    <td style="padding: 0 10px; text-align: center;">
                                        <div style="font-size: 8pt; color: #666; margin-bottom: 3px;">SECONDARY</div>
                                        <table style="table-layout: fixed; margin: 0 auto;"><tr>
                                            <td bgcolor="#F15A24" align="center" style="color: white; padding: 5px 10px; font-size: 10pt; font-weight: bold; min-width: 80px;">{disc_secondary}</td>
                                        </tr></table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
                
                <table width="100%" style="table-layout: fixed; margin-top: 10px;"><tr>
                    <td bgcolor="#F4F6F9" style="padding: 10px 12px; font-size: 9pt; line-height: 1.4; color: #444; border-left: 4px solid #1B365D;"><strong>Karakter Utama ({disc_primary}):</strong> {disc_primary_desc}
                    <br style="margin-bottom: 4px;"/>
                    <strong>Karakter Pendukung ({disc_secondary}):</strong> {disc_secondary_desc}</td>
                </tr></table>
            </div>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">CLICK FINGER CONSULTING</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 4</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 5: LEARNING STYLE (VAK) -->
    <div class="page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Learning Style / Gaya Belajar</td>
            </tr></table>
            <div class="participant-highlight">Kombinasi Gaya Belajar (VAK): <span>{participant_name}</span></div>
            
            <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px;">
                <tr>
                    <td width="140" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">VISUAL</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                            <tr>
                                <td width="{vak_visual}%" bgcolor="#1B365D" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                <td bgcolor="#F4F6F9" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                            </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{vak_visual}%</td>
                </tr>
                <tr>
                    <td width="140" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">AUDITORI</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                            <tr>
                                <td width="{vak_auditori}%" bgcolor="#F15A24" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                <td bgcolor="#F4F6F9" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                            </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{vak_auditori}%</td>
                </tr>
                <tr>
                    <td width="140" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">KINESTETIK</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                            <tr>
                                <td width="{vak_kinestetik}%" bgcolor="#1B365D" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                <td bgcolor="#F4F6F9" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                            </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{vak_kinestetik}%</td>
                </tr>
            </table>
            
            <table width="100%" style="table-layout: fixed; margin-top: 10px;"><tr>
                <td bgcolor="#F4F6F9" style="padding: 10px 12px; font-size: 9pt; line-height: 1.4; color: #444; border-left: 4px solid #1B365D;"><strong>Saran Metode Belajar Terbimbing:</strong><br>
                Anda memiliki kecenderungan gaya belajar dominan <strong>{dominant_vak}</strong>. Untuk hasil belajar yang maksimal, disarankan untuk {vak_learning_advice}</td>
            </tr></table>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">CLICK FINGER CONSULTING</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 5</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 6: MULTIPLE QUOTIENT -->
    <div class="page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Multiple Quotient / Kecerdasan Psikologis</td>
            </tr></table>
            <div class="participant-highlight">Distribusi Quotient Psikologis: <span>{participant_name}</span></div>
            
            <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px;">
                <tr>
                    <td width="150" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">IQ (Intellectual)</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                            <tr>
                                <td width="{iq_pct}%" bgcolor="#1B365D" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                <td bgcolor="#F4F6F9" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                            </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{iq_pct}%</td>
                </tr>
                <tr>
                    <td width="150" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">EQ (Emotional)</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                            <tr>
                                <td width="{eq_pct}%" bgcolor="#F15A24" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                <td bgcolor="#F4F6F9" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                            </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{eq_pct}%</td>
                </tr>
                <tr>
                    <td width="150" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">CQ (Creative)</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                            <tr>
                                <td width="{cq_pct}%" bgcolor="#1B365D" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                <td bgcolor="#F4F6F9" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                            </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{cq_pct}%</td>
                </tr>
                <tr>
                    <td width="150" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">AQ (Adversity)</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                            <tr>
                                <td width="{aq_pct}%" bgcolor="#F15A24" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                <td bgcolor="#F4F6F9" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                            </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{aq_pct}%</td>
                </tr>
            </table>
            
            <table width="100%" style="table-layout: fixed; margin-top: 10px;"><tr>
                <td bgcolor="#F4F6F9" style="padding: 10px 12px; font-size: 9pt; line-height: 1.4; color: #444; border-left: 4px solid #1B365D;"><strong>Keseimbangan Aspek Psikologis:</strong><br>
                Quotient tertinggi Anda berada pada <strong>{top_quotient}</strong>. Ini menandakan kemampuan yang sangat baik dalam {top_quotient_desc}.</td>
            </tr></table>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">CLICK FINGER CONSULTING</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 6</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 7: ADAPTABILITAS KEPRIBADIAN -->
    <div class="page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Adaptabilitas Kepribadian</td>
            </tr></table>
            <div class="participant-highlight">Pola Adaptabilitas Kepribadian: <span>{participant_name}</span></div>
            
            <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px;">
                <tr>
                    <td width="150" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">SELF KOGNITIF</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                            <tr>
                                <td width="{adaptability_kognitif}%" bgcolor="#1B365D" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                <td bgcolor="#F4F6F9" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                            </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{adaptability_kognitif}%</td>
                </tr>
                <tr>
                    <td width="150" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">AFEKTIF</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                            <tr>
                                <td width="{adaptability_afektif}%" bgcolor="#F15A24" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                <td bgcolor="#F4F6F9" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                            </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{adaptability_afektif}%</td>
                </tr>
                <tr>
                    <td width="150" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">REFLEKTIF</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                            <tr>
                                <td width="{adaptability_reflektif}%" bgcolor="#1B365D" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                <td bgcolor="#F4F6F9" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                            </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{adaptability_reflektif}%</td>
                </tr>
                <tr>
                    <td width="150" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">KRITIS</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                            <tr>
                                <td width="{adaptability_kritis}%" bgcolor="#F15A24" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                <td bgcolor="#F4F6F9" style="height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                            </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{adaptability_kritis}%</td>
                </tr>
            </table>
            
            <table width="100%" style="table-layout: fixed; margin-top: 10px;"><tr>
                <td bgcolor="#F4F6F9" style="padding: 10px 12px; font-size: 9pt; line-height: 1.4; color: #444; border-left: 4px solid #1B365D;"><strong>Gaya Penyesuaian Diri Utama:</strong><br>
                {adaptability_desc}
                <br style="margin-bottom: 4px;"/>
                <em>Catatan: Nilai Reflektif dan Kritis yang rendah merupakan hal wajar dan bukan masalah, karena fungsi adaptabilitas dipengaruhi oleh karakter dan kematangan kepribadian yang telah terbentuk.</em></td>
            </tr></table>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">CLICK FINGER CONSULTING</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 7</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 8: REFERENSI EKSTRAKURIKULER & LOVE LANGUAGE -->
    <div class="page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Referensi Ekstrakurikuler & Love Language</td>
            </tr></table>
            <div class="participant-highlight">Aktivitas Tambahan & Bahasa Cinta: <span>{participant_name}</span></div>
            
            <!-- Extracurriculars Table -->
            <div>
                <table width="100%" style="table-layout: fixed; margin-bottom: 8px;"><tr>
                    <td bgcolor="#F4F6F9" style="padding: 5px 10px; font-size: 10pt; font-weight: bold; color: #1B365D; text-transform: uppercase; border-left: 4px solid #F15A24;">1. Pilihan Ekstrakurikuler</td>
                </tr></table>
                {extracurriculars_table}
                <div style="font-size: 8pt; color: #666; margin-top: 4px; text-align: center;">
                    Urutan 1-6: Sangat Direkomendasikan | 7-11: Cukup Direkomendasikan | 12-16: Kurang Direkomendasikan
                </div>
            </div>
            
            <!-- Love Language Section -->
            <div style="margin-top: 10px;">
                <table width="100%" style="table-layout: fixed; margin-bottom: 8px;"><tr>
                    <td bgcolor="#F4F6F9" style="padding: 5px 10px; font-size: 10pt; font-weight: bold; color: #1B365D; text-transform: uppercase; border-left: 4px solid #F15A24;">2. Love Language (Bahasa Cinta)</td>
                </tr></table>
                
                <table width="100%" style="table-layout: fixed; margin-top: 10px;"><tr>
                    <td bgcolor="#F4F6F9" style="padding: 10px 12px; font-size: 9pt; line-height: 1.4; color: #444; border-left: 4px solid #1B365D;"><strong>Bahasa Cinta Dominan ({love_language_primary}):</strong><br>
                    {love_language_desc}
                    <br style="margin-bottom: 2px;"/>
                    <em>Tips: Cinta = Usaha Kecil Tapi Konsisten. Tenang dan teliti. Merasa disayang bila dibantu dengan tertib dan diperhatikan kebutuhannya. 👉 Tidak perlu berlebihan, yang penting konsisten.</em></td>
                </tr></table>
            </div>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">CLICK FINGER CONSULTING</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 8</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 9: REFERENSI AKADEMIK & KARIR -->
    <div class="page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Referensi Akademik & Karir</td>
            </tr></table>
            <div class="participant-highlight">Bidang Studi & Profesi Pilihan: <span>{participant_name}</span></div>
            
            <div style="margin-top: 5px;">
                {careers_table}
                <div style="font-size: 8pt; color: #666; margin-top: 8px; text-align: center;">
                    Urutan 1-20: Sangat Direkomendasikan | 21-40: Cukup Direkomendasikan | 41-60: Kurang Direkomendasikan
                </div>
            </div>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">CLICK FINGER CONSULTING</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 9</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 10: KESIMPULAN & SARAN -->
    <div class="page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Kesimpulan & Saran Pengembangan</td>
            </tr></table>
            <div class="participant-highlight">Kesimpulan Hasil Evaluasi: <span>{participant_name}</span></div>
            
            <div style="font-size: 7.4pt; line-height: 1.25; color: #444; overflow: hidden; display: block; margin-top: 6px;">
                <div style="margin-bottom: 6px; padding-bottom: 2px;">
                    <strong>Multiple Intelligence:</strong> {conclusion_intelligence}
                </div>
                <hr style="border: none; height: 1px; background-color: #F15A24; margin: 4px 0;">
                <div style="margin-bottom: 6px; padding-bottom: 2px;">
                    <strong>Tipe Kepribadian DISC:</strong> {conclusion_personality}
                </div>
                <hr style="border: none; height: 1px; background-color: #F15A24; margin: 4px 0;">
                <div style="margin-bottom: 6px; padding-bottom: 2px;">
                    <strong>Bahasa Cinta (Love Language):</strong> {love_language_desc}
                </div>
                <hr style="border: none; height: 1px; background-color: #F15A24; margin: 4px 0;">
                <div style="margin-bottom: 6px; padding-bottom: 2px;">
                    <strong>Brain Dominance & Gaya Belajar:</strong> Dominasi {dominant_brain} Brain ({left_brain_pct}% kiri vs {right_brain_pct}% kanan) menunjukkan kecenderungan cara berpikir {dominant_brain}. {conclusion_vak}
                </div>
                <hr style="border: none; height: 1px; background-color: #F15A24; margin: 4px 0;">
                <div style="margin-bottom: 6px; padding-bottom: 2px;">
                    <strong>Adaptabilitas & Kecerdasan Psikologis:</strong> {conclusion_adaptability} {conclusion_quotient}
                </div>
            </div>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">CLICK FINGER CONSULTING</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 10</td>
                </tr></table>
            </div>
        </div>
    </div>

</body>
</html>
"""

# Hardcoded static descriptions and references for building the report
INTELLIGENCE_DESCS = {
    "intrapersonal": "Kecerdasan memahami diri sendiri, emosi, motivasi, dan kekuatan internal.",
    "logical": "Kecerdasan berpikir logis, pemecahan masalah, angka, pola, dan struktur.",
    "linguistik": "Kecerdasan memahami bahasa, verbal, penjelasan lisan, dan instruksi tertulis.",
    "naturalis": "Kecerdasan kepekaan terhadap lingkungan, alam, hewan, dan observasi visual.",
    "interpersonal": "Kecerdasan berinteraksi, bekerja sama, berempati, dan menyesuaikan diri secara sosial.",
    "visual-spasial": "Kecerdasan memproses visual, gambar, warna, desain, dan orientasi ruang.",
    "kinestetik": "Kecerdasan belajar melalui gerakan, aktivitas fisik, motorik kasar/halus, dan praktek.",
    "musikal": "Kecerdasan kepekaan terhadap suara, irama, nada, ketukan, dan pengekspresian kreatif."
}

DISC_DESCS = {
    "Dominan": (
        "Individu cenderung tegas, keras, mandiri, berani mengambil keputusan, "
        "dan memiliki dorongan kuat untuk mencapai tujuan. Ia biasanya cepat bertindak "
        "dan suka tantangan serta berjiwa pemimpin, percaya diri dan bertanggung jawab, "
        "namun terkadang perlu diingatkan untuk mempertimbangkan perasaan orang lain."
    ),
    "Influential": (
        "Individu cenderung memiliki potensi tak terbatas, ramah, ekspresif, "
        "dan mudah berinteraksi dengan lingkungan sekitarnya. Ia menikmati komunikasi, "
        "perhatian, dan suasana yang menyenangkan, serta lebih mudah berkembang dalam "
        "hubungan sosial yang positif. Butuh dukungan untuk tampil serta membutuhkan "
        "panduan namun kurang dalam pengaturan waktu."
    ),
    "Steady": (
        "Individu cenderung tenang dan menyukai suasana yang stabil serta teratur. "
        "Ia membutuhkan rasa aman, rutinitas yang jelas, dan waktu untuk beradaptasi, "
        "serta biasanya menunjukkan sikap yang konsisten dan penuh pertimbangan serta "
        "menghindari konflik & konfrontasi."
    ),
    "Compliant": (
        "Individu cenderung analitis, teliti, berhati-hati, dan memperhatikan aturan "
        "atau detail. Nyaman dengan struktur yang jelas dan membutuhkan penjelasan "
        "yang runtut agar merasa yakin sebelum bertindak. Perencana yang hebat dan "
        "perfeksionis, namun butuh waktu dalam mengambil keputusan."
    )
}

STIMULATION_TIPS = {
    "intrapersonal": (
        "Biarkan anak mengerjakan sesuatu yang dia mampu lakukan sendiri (tidak selalu dibantu), "
        "Berikan suatu pilihan dan biarkan anak untuk memutuskannya, memberikan pertanyaan yang "
        "jawabannya bukan ya atau tidak saja, memberikan sesekali waktu untuk mereka sendiri & "
        "belajar menulis jurnal harian"
    ),
    "logical": (
        "Latihan dalam berhitung, memainkan permainan logika & strategi, belajar pola & grafik, "
        "ajukan pertanyaan \"Mengapa\" & \"Bagaimana\", eksperimen sains sederhana"
    ),
    "linguistik": (
        "Rutin membaca buku, menulis cerita atau jurnal, latihan bercerita atau presentasi, "
        "mendengarkan cerita atau audiobook, bermain kata & bahasa, belajar bahasa asing sejak dini"
    ),
    "naturalis": (
        "Berkebun & merawat tanaman, mengamati hewan sekitar, mengenali cuaca & perubahan alam, "
        "melakukan kegiatan di alam terbuka"
    ),
    "interpersonal": (
        "Ikut aktif serta dalam kegiatan sosial atau organisasi, berlatih presentasi atau bercerita "
        "di depan orang, sering ajak untuk berdiskusi, berikan peran sebagai penolong atau mediator"
    ),
    "visual-spasial": (
        "Berlatih menggambar & mewarnai, bermain puzzle/lego, membaca buku bergambar, "
        "membaca dan membuat peta/denah, mengamati pola, simetri & bayangan dan sering "
        "menggunakan aplikasi desain atau permainan edukatif lainnya"
    ),
    "kinestetik": (
        "Ajak untuk aktif bergerak, aktivitas motorik halus seperti membuat origami dan sejenisnya, "
        "beraktifitas dengan menggunakan alat seperti lompat tali/bola/sepeda dan berlatih "
        "keseimbangan serta kelenturan seperti senam dan sejenisnya"
    ),
    "musikal": (
        "Belajar memainkan alat musik, bernyanyi bersama, memperdengarkan musik yang sesuai "
        "dengan usianya, ajak menonton konser atau pertunjukkan musik dan belajar membedakan "
        "nada serta alat musik"
    )
}

LOVE_LANGUAGE_DESCS = {
    "Acts of Service": {
        "title": "Acts of Service (Cinta Tersampaikan Lewat Perbuatan Nyata)",
        "desc": (
            "Merasa disayang bila dibantu dengan tertib dan diperhatikan kebutuhannya. "
            "Tindakan nyata yang membantu meringankan beban atau mempermudah aktivitasnya akan sangat berarti."
        )
    },
    "Quality Time": {
        "title": "Quality Time (Cinta Tersampaikan Lewat Waktu & Perhatian Penuh)",
        "desc": (
            "Merasa dihargai melalui kehadiran secara penuh, percakapan mendalam, dan "
            "aktivitas bersama tanpa adanya distraksi (seperti gawai atau pekerjaan)."
        )
    },
    "Receiving Gifts": {
        "title": "Receiving Gifts (Cinta Tersampaikan Lewat Pemberian)",
        "desc": (
            "Melihat hadiah sebagai bentuk perhatian dan kasih sayang yang tulus dari "
            "pemberinya, bukan didasarkan pada nilai materi barang tersebut."
        )
    },
    "Words of Affirmation": {
        "title": "Words of Affirmation (Cinta Tersampaikan Lewat Kata-kata Positif)",
        "desc": (
            "Sangat menghargai pujian, kata-kata penyemangat, ungkapan kasih sayang, "
            "dan pengakuan verbal atas usaha yang telah dilakukannya."
        )
    },
    "Physical Touch": {
        "title": "Physical Touch (Cinta Tersampaikan Lewat Sentuhan Fisik)",
        "desc": (
            "Merasakan kedekatan emosional dan rasa aman melalui kontak fisik seperti "
            "pelukan, genggaman tangan, usapan di kepala, atau rangkulan hangat."
        )
    }
}

EXTRACURRICULARS = [
    {"name": "Musik / Band", "cat": "musikal"},
    {"name": "Seni Tari / Modern Dance", "cat": "kinestetik"},
    {"name": "Kerohanian / Keagamaan", "cat": "intrapersonal"},
    {"name": "English Club", "cat": "linguistik"},
    {"name": "Theater / Drama", "cat": "linguistik"},
    {"name": "Sastra", "cat": "linguistik"},
    {"name": "Palang Merah Remaja (PMR)", "cat": "interpersonal"},
    {"name": "Pramuka", "cat": "kinestetik"},
    {"name": "Basket / Sepakbola/ Bulutangkis", "cat": "kinestetik"},
    {"name": "Renang", "cat": "kinestetik"},
    {"name": "Melukis / Mewarnai", "cat": "visual-spasial"},
    {"name": "Memanah", "cat": "kinestetik"},
    {"name": "Paduan Suara", "cat": "musikal"},
    {"name": "Beladiri", "cat": "kinestetik"},
    {"name": "Fotografi", "cat": "visual-spasial"},
    {"name": "Robotika & Komputer", "cat": "logical"}
]

CAREERS = [
    {"name": "Sosiologi", "cat": "interpersonal"},
    {"name": "Antropologi", "cat": "naturalis"},
    {"name": "Seni Musik", "cat": "musikal"},
    {"name": "Enterpreneurship", "cat": "intrapersonal"},
    {"name": "Manajemen", "cat": "intrapersonal"},
    {"name": "Jurnalistik", "cat": "linguistik"},
    {"name": "Filsafat", "cat": "intrapersonal"},
    {"name": "Ilmu Pendidikan Agama", "cat": "intrapersonal"},
    {"name": "Sastra/Literatur", "cat": "linguistik"},
    {"name": "Bahasa Asing", "cat": "linguistik"},
    {"name": "Akuntansi", "cat": "logical"},
    {"name": "Psikologi", "cat": "interpersonal"},
    {"name": "Bisnis Manajemen", "cat": "intrapersonal"},
    {"name": "Seni Peran", "cat": "linguistik"},
    {"name": "Ilmu Komunikasi", "cat": "interpersonal"},
    {"name": "Ilmu Politik", "cat": "interpersonal"},
    {"name": "Hubungan Internasional", "cat": "interpersonal"},
    {"name": "Seni Tari", "cat": "kinestetik"},
    {"name": "Ilmu Kehutanan", "cat": "naturalis"},
    {"name": "Bioteknologi", "cat": "logical"},
    {"name": "Keperawatan", "cat": "interpersonal"},
    {"name": "Ilmu Hukum", "cat": "logical"},
    {"name": "Ilmu Pendidikan Biologi", "cat": "naturalis"},
    {"name": "Teknik Sipil", "cat": "visual-spasial"},
    {"name": "Administrasi Niaga", "cat": "logical"},
    {"name": "Business Analyst", "cat": "logical"},
    {"name": "Perhotelan & Pariwisata", "cat": "interpersonal"},
    {"name": "Ilmu Pendidikan Guru", "cat": "interpersonal"},
    {"name": "Insurance", "cat": "logical"},
    {"name": "Ilmu Perpajakan", "cat": "logical"},
    {"name": "Polisi", "cat": "kinestetik"},
    {"name": "Kedokteran", "cat": "logical"},
    {"name": "Teknik Informatika", "cat": "logical"},
    {"name": "Teknik Komputer", "cat": "logical"},
    {"name": "Tata Boga", "cat": "kinestetik"},
    {"name": "Ilmu Pendidikan Olahraga", "cat": "kinestetik"},
    {"name": "Desain Busana/Mode", "cat": "visual-spasial"},
    {"name": "Teknik Kimia", "cat": "logical"},
    {"name": "Arkeologi", "cat": "naturalis"},
    {"name": "Patologi", "cat": "logical"},
    {"name": "Angkatan Darat", "cat": "kinestetik"},
    {"name": "Angkatan Laut", "cat": "kinestetik"},
    {"name": "Teknik Elektro", "cat": "logical"},
    {"name": "Angkatan Udara", "cat": "kinestetik"},
    {"name": "Photography", "cat": "visual-spasial"},
    {"name": "Teknik Industri", "cat": "logical"},
    {"name": "Teknik Mesin", "cat": "logical"},
    {"name": "Fire Rescue", "cat": "kinestetik"},
    {"name": "Farmasi", "cat": "logical"},
    {"name": "Ilmu Geologi", "cat": "naturalis"},
    {"name": "Teknik Fisika", "cat": "logical"},
    {"name": "Agrikultur Perkebunan", "cat": "naturalis"},
    {"name": "Statistika", "cat": "logical"},
    {"name": "Nutritionist", "cat": "naturalis"},
    {"name": "Teknik Lingkungan", "cat": "naturalis"},
    {"name": "Ilmu Pertanahan", "cat": "naturalis"},
    {"name": "Ilmu Peternakan", "cat": "naturalis"},
    {"name": "Ilmu Perikanan", "cat": "naturalis"},
    {"name": "Ekonomi & Akutansi", "cat": "logical"},
    {"name": "Ilmu Matematika", "cat": "logical"}
]

class HTMLReportGenerator:
    @staticmethod
    def calculate_dmit_metrics(features_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert raw fingerprint features into full normalized DMIT scores."""
        # Initialize default weights to avoid divide-by-zero
        finger_weights = {
            "left_thumb": 10.0, "left_index": 10.0, "left_middle": 10.0, "left_ring": 10.0, "left_pinky": 10.0,
            "right_thumb": 10.0, "right_index": 10.0, "right_middle": 10.0, "right_ring": 10.0, "right_pinky": 10.0
        }
        
        # Override weights with actual ridge counts if present
        for f in features_list:
            pos = f.get("finger_position")
            rc = f.get("ridge_count") or 0
            if pos in finger_weights and rc > 0:
                finger_weights[pos] = float(rc)
                
        total_weight = sum(finger_weights.values())
        
        # 1. Gardner Intelligences mapping
        intel_raw = {
            "intrapersonal": finger_weights["right_thumb"],
            "interpersonal": finger_weights["left_thumb"],
            "logical": finger_weights["right_index"],
            "visual-spasial": finger_weights["left_index"],
            "kinestetik": (finger_weights["left_middle"] + finger_weights["right_middle"]) / 2.0,
            "musikal": finger_weights["left_ring"],
            "linguistik": finger_weights["right_ring"],
            "naturalis": (finger_weights["left_pinky"] + finger_weights["right_pinky"]) / 2.0
        }
        
        # Normalize intelligences to sum to 100%
        total_intel = sum(intel_raw.values())
        intel_pcts = {k: round((v / total_intel) * 100, 2) for k, v in intel_raw.items()}
        
        # 2. Quotients mapping (IQ, EQ, CQ, AQ)
        iq = intel_pcts["logical"] + intel_pcts["linguistik"]
        eq = intel_pcts["interpersonal"] + intel_pcts["intrapersonal"]
        cq = intel_pcts["visual-spasial"] + intel_pcts["musikal"]
        aq = intel_pcts["kinestetik"] + intel_pcts["naturalis"]
        
        total_q = iq + eq + cq + aq
        q_pcts = {
            "IQ": round((iq / total_q) * 100, 2),
            "EQ": round((eq / total_q) * 100, 2),
            "CQ": round((cq / total_q) * 100, 2),
            "AQ": round((aq / total_q) * 100, 2)
        }
        
        # 3. Brain Dominance
        left_brain_raw = sum(finger_weights[f] for f in ["right_thumb", "right_index", "right_middle", "right_ring", "right_pinky"])
        right_brain_raw = sum(finger_weights[f] for f in ["left_thumb", "left_index", "left_middle", "left_ring", "left_pinky"])
        total_brain = left_brain_raw + right_brain_raw
        
        brain_pcts = {
            "left": round((left_brain_raw / total_brain) * 100, 2),
            "right": round((right_brain_raw / total_brain) * 100, 2)
        }
        
        # 4. Learning Styles (VAK)
        visual_raw = intel_pcts["visual-spasial"] + intel_pcts["naturalis"]
        auditori_raw = intel_pcts["linguistik"] + intel_pcts["musikal"]
        kinestetik_raw = intel_pcts["kinestetik"] + (intel_pcts["interpersonal"] / 3.0) # add interpersonal weight to physical
        
        total_vak = visual_raw + auditori_raw + kinestetik_raw
        vak_pcts = {
            "visual": round((visual_raw / total_vak) * 100, 2),
            "auditori": round((auditori_raw / total_vak) * 100, 2),
            "kinestetik": round((kinestetik_raw / total_vak) * 100, 2)
        }
        
        # 5. Adaptability (Kognitif, Afektif, Reflektif, Kritis)
        kognitif = round(brain_pcts["left"] / 10.0) * 10.0
        afektif = 100.0 - kognitif
        reflektif = 0.0
        kritis = 0.0
        adaptability_pcts = {
            "kognitif": kognitif,
            "afektif": afektif,
            "reflektif": reflektif,
            "kritis": kritis
        }
        
        return {
            "intelligences": intel_pcts,
            "quotients": q_pcts,
            "brain": brain_pcts,
            "vak": vak_pcts,
            "adaptability": adaptability_pcts
        }

    @classmethod
    def generate_html_report(cls, participant_name: str, features_list: List[Dict[str, Any]]) -> str:
        """Process results and format the rich HTML template."""
        metrics = cls.calculate_dmit_metrics(features_list)
        
        # Sort intelligences to find strengths
        sorted_intel = sorted(metrics["intelligences"].items(), key=lambda x: x[1], reverse=True)
        top_int_1 = sorted_intel[0][0].upper()
        top_int_2 = sorted_intel[1][0].upper()
        
        # Display name mapping for Indonesian
        intel_display_names = {
            "intrapersonal": "Intrapersonal",
            "logical": "Logical",
            "linguistik": "Linguistik",
            "naturalis": "Naturalis",
            "interpersonal": "Interpersonal",
            "visual-spasial": "Visual-Spasial",
            "kinestetik": "Kinestetik",
            "musikal": "Musikal"
        }
        
        # Build intelligence rows for Page 2
        intel_rows_html = '<table style="table-layout: fixed; width: 100%; border-collapse: collapse; margin-top: 5px;">\n'
        for i, (name, val) in enumerate(sorted_intel):
            bg_color = "#fdfdfd" if i % 2 == 0 else "#F4F6F9"
            desc = INTELLIGENCE_DESCS.get(name, "")
            display_name = intel_display_names.get(name, name.capitalize())
            label_bg = "#F15A24" if i % 2 == 0 else "#1B365D"
            
            intel_rows_html += f"""  <tr style="background-color: {bg_color}; border: 1px solid #e9eff4;">
    <td width="65" style="font-size: 12pt; font-weight: 800; color: #1B365D; padding: 5px 8px; vertical-align: middle;">{val}%</td>
    <td width="135" style="padding: 5px 8px; vertical-align: middle;">
      <div style="background-color: {label_bg}; color: white; padding: 3px 6px; text-align: center; font-size: 9.5pt; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">{display_name}</div>
    </td>
    <td style="font-size: 8.5pt; line-height: 1.3; color: #555; padding: 5px 8px; vertical-align: middle;">{desc}</td>
  </tr>\n"""
        intel_rows_html += "</table>"
            
        # Build stimulation tips for Page 3 (using a 2-column table to fit comfortably on 1 page)
        stimulation_tips_html = '<table width="100%" style="table-layout: fixed; border-collapse: separate; border-spacing: 8px 0px;">\n'
        for r in range(4):
            idx1 = r
            idx2 = r + 4
            name1, _ = sorted_intel[idx1]
            name2, _ = sorted_intel[idx2]
            
            tips1 = STIMULATION_TIPS.get(name1, "")
            tips2 = STIMULATION_TIPS.get(name2, "")
            
            display_name1 = intel_display_names.get(name1, name1.upper()).upper()
            display_name2 = intel_display_names.get(name2, name2.upper()).upper()
            
            border_color1 = "#F15A24" if idx1 % 2 == 0 else "#1B365D"
            border_color2 = "#F15A24" if idx2 % 2 == 0 else "#1B365D"
            
            label_color1 = "#F15A24" if idx1 % 2 == 0 else "#1B365D"
            label_color2 = "#F15A24" if idx2 % 2 == 0 else "#1B365D"
            
            stimulation_tips_html += f"""  <tr>
    <td width="50%" style="vertical-align: top; padding-bottom: 3px;">
      <div style="border-left: 3px solid {border_color1}; padding-left: 5px;">
        <div style="font-size: 7.5pt; font-weight: bold; color: {label_color1}; margin-bottom: 1px;">{display_name1}</div>
        <div style="font-size: 7pt; line-height: 1.25; color: #444;">{tips1}</div>
      </div>
    </td>
    <td width="50%" style="vertical-align: top; padding-bottom: 3px;">
      <div style="border-left: 3px solid {border_color2}; padding-left: 5px;">
        <div style="font-size: 7.5pt; font-weight: bold; color: {label_color2}; margin-bottom: 1px;">{display_name2}</div>
        <div style="font-size: 7pt; line-height: 1.25; color: #444;">{tips2}</div>
      </div>
    </td>
  </tr>\n"""
        stimulation_tips_html += "</table>"
            
        # DISC mapping
        disc_primary = "Steady"
        disc_secondary = "Compliant"
        # Dynamic check if logical/analytical is extremely high
        if metrics["intelligences"]["logical"] > 15:
            disc_primary = "Compliant"
            disc_secondary = "Steady"
            
        # Brain Dominance details
        left_brain_pct = metrics["brain"]["left"]
        right_brain_pct = metrics["brain"]["right"]
        dominant_brain = "Left" if left_brain_pct > right_brain_pct else "Right"
        brain_desc = (
            "Anda cenderung menggunakan cara berpikir yang logis, terstruktur, analitis, "
            "dan bertahap. Anda sangat menyukai kejelasan informasi dan urutan langkah yang runtut."
            if dominant_brain == "Left" else
            "Anda cenderung menggunakan cara berpikir yang kreatif, intuitif, imajinatif, "
            "dan holistik. Anda lebih mudah memahami informasi visual atau kontekstual melalui pengalaman."
        )
        
        # VAK details
        vak = metrics["vak"]
        sorted_vak = sorted(vak.items(), key=lambda x: x[1], reverse=True)
        dominant_vak = sorted_vak[0][0].upper()
        
        vak_advices = {
            "VISUAL": "menyajikan materi dalam bentuk gambar, diagram, infografis, warna, atau mind map yang jelas.",
            "AUDITORI": "menjelaskan secara lisan, memicu diskusi kelompok, merekam suara penjelasan, dan melakukan tanya jawab.",
            "KINESTETIK": "melakukan praktek langsung, melakukan eksperimen, belajar sambil bergerak, serta menghindari duduk diam terlalu lama."
        }
        vak_advice = vak_advices.get(dominant_vak, "pendekatan pembelajaran yang bervariasi.")
        
        # Quotients details
        sorted_q = sorted(metrics["quotients"].items(), key=lambda x: x[1], reverse=True)
        top_q = sorted_q[0][0]
        q_descs = {
            "IQ": "kemampuan pemecahan masalah secara logis, analisis angka, dan pemahaman verbal.",
            "EQ": "kemampuan berempati, memahami emosi diri, bersosialisasi, dan menjaga hubungan baik.",
            "CQ": "kemampuan berpikir 'out-of-the-box', memunculkan ide-ide inovatif, dan pengekspresian seni.",
            "AQ": "kemampuan bertahan dalam tantangan, ketangguhan mental, dan ketahanan terhadap stress."
        }
        top_q_desc = q_descs.get(top_q, "pengelolaan kecerdasan mental.")
        
        # Adaptability details
        adaptability = metrics["adaptability"]
        adaptability_desc = (
            "Cenderung menyesuaikan diri dengan cara memahami situasi yang dihadapi. "
            "Ia berusaha menangkap maksud dan kondisi terlebih dahulu sebelum merespons, "
            "sehingga terlihat cukup tenang dan terarah saat menghadapi perubahan. "
            "Pendampingan akan lebih efektif bila diberikan penjelasan yang jelas "
            "dan kesempatan untuk memahami situasi secara bertahap."
        )
        
        # Love Language mapping based on DISC
        love_language_primary = "Acts of Service"
        if disc_primary == "Dominan":
            love_language_primary = "Words of Affirmation"
        elif disc_primary == "Influential":
            love_language_primary = "Quality Time"
        elif disc_primary == "Steady":
            love_language_primary = "Acts of Service"
        elif disc_primary == "Compliant":
            love_language_primary = "Receiving Gifts"
            
        love_language_desc = LOVE_LANGUAGE_DESCS.get(love_language_primary, {}).get("desc", "")
        love_language_title = LOVE_LANGUAGE_DESCS.get(love_language_primary, {}).get("title", love_language_primary)
        
        # Recommendations sorting & classification
        intel_ranks = {name: rank for rank, (name, _) in enumerate(sorted_intel)}
        
        def get_rank_class(item_cat):
            rank = intel_ranks.get(item_cat, 4)
            if rank <= 2:
                return "green"
            elif rank <= 5:
                return "orange"
            return "red"
            
        # Build 2-column table for Extracurriculars
        sorted_ex = sorted(EXTRACURRICULARS, key=lambda x: intel_ranks.get(x["cat"], 10))
        extracurriculars_table = '<table class="rec-table" width="100%" style="table-layout: fixed;">\n'
        for i in range(8):
            ex1 = sorted_ex[i]
            ex2 = sorted_ex[i + 8]
            
            rank_class1 = get_rank_class(ex1["cat"])
            rank_class2 = get_rank_class(ex2["cat"])
            
            extracurriculars_table += f"""  <tr>
    <td class="{rank_class1}" width="50%">{i+1}. {ex1["name"]},</td>
    <td class="{rank_class2}" width="50%">{i+9}. {ex2["name"]},</td>
  </tr>\n"""
        extracurriculars_table += "</table>"
        
        # Build 5-column table for Careers
        sorted_cr = sorted(CAREERS, key=lambda x: intel_ranks.get(x["cat"], 10))
        careers_table = '<table class="rec-table" width="100%" style="table-layout: fixed; border-spacing: 4px;">\n'
        for r in range(12):
            careers_table += "  <tr>\n"
            for c in range(5):
                idx = r * 5 + c
                cr = sorted_cr[idx]
                rank_class = get_rank_class(cr["cat"])
                careers_table += f'    <td class="{rank_class}" width="20%" style="padding: 4px 6px; font-size: 7.5pt;">{idx+1}. {cr["name"]},</td>\n'
            careers_table += "  </tr>\n"
        careers_table += "</table>"
        
        # Page 10 Conclusion content preparation
        indonesian_intels_good = [intel_display_names[name] for name, val in metrics["intelligences"].items() if val >= 9.0]
        indonesian_intels_low = [intel_display_names[name] for name, val in metrics["intelligences"].items() if val < 9.0]
        
        if len(indonesian_intels_good) >= 6:
            conclusion_intelligence = (
                "Kecerdasan berkembang relatif merata di berbagai area. Memiliki fleksibilitas dalam merespons berbagai situasi "
                "dan dapat menyesuaikan diri dengan beragam pendekatan. Pendampingan yang bervariasi dan konsisten akan membantu "
                "perkembangan secara lebih menyeluruh. "
            )
        else:
            conclusion_intelligence = (
                f"Kecerdasan berkembang secara lebih terfokus pada kekuatan utama Anda di bidang {top_int_1.capitalize()} dan {top_int_2.capitalize()}. "
            )
        
        if indonesian_intels_good:
            conclusion_intelligence += f"Kecerdasan {', '.join(indonesian_intels_good)} berperan sebagai pendukung dan dapat terus berkembang dengan pendampingan yang sesuai. "
        if indonesian_intels_low:
            conclusion_intelligence += f"Sementara itu, area kecerdasan {', '.join(indonesian_intels_low)} masih membutuhkan stimulasi agar perkembangan berjalan lebih seimbang."
            
        p_desc = DISC_DESCS[disc_primary].replace("Individu cenderung", "Dalam keseharian, cenderung")
        s_desc = DISC_DESCS[disc_secondary].replace("Individu cenderung", "Pada situasi tertentu, juga menunjukkan sikap yang")
        conclusion_personality = f"{p_desc} {s_desc} Secara umum, individu dapat berkembang dengan baik ketika didampingi secara konsisten dan diberikan ruang untuk mengekspresikan diri dengan caranya sendiri."
        
        sec_vak = sorted_vak[1][0].upper()
        vak_details = {
            "VISUAL": "Lebih mudah memahami informasi melalui visual, gambar, diagram, dan contoh yang dapat dilihat secara langsung. Informasi cenderung lebih mudah diingat bila disertai tampilan visual yang jelas, rapi, dan terstruktur. Penjelasan tanpa bantuan visual sering kali membuat pemahaman menjadi kurang optimal.",
            "AUDITORI": "Lebih mudah memahami informasi melalui penjelasan lisan, percakapan, dan pengulangan. Pendampingan akan lebih optimal bila disampaikan dengan intonasi yang jelas, diskusi ringan, serta memberi kesempatan individu untuk mendengar dan bertanya.",
            "KINESTETIK": "Lebih mudah memahami informasi melalui aktivitas langsung dan keterlibatan gerak. Pendampingan akan lebih efektif bila individu diberi kesempatan untuk mencoba, mempraktikkan, dan belajar sambil melakukan secara langsung."
        }
        conclusion_vak = (
            f"Cenderung lebih nyaman dengan Gaya Belajar {dominant_vak.capitalize()}, dengan dukungan Gaya Belajar {sec_vak.capitalize()}. "
            f"{vak_details[dominant_vak]} Selain itu, Gaya Belajar pendukung turut membantu dalam memahami informasi dengan lebih fleksibel. "
            f"{vak_details[sec_vak]}"
        )
        
        conclusion_adaptability = (
            "Cenderung menyesuaikan diri dengan cara memahami situasi yang dihadapi. Ia berusaha menangkap maksud dan kondisi terlebih dahulu "
            "sebelum merespons, sehingga terlihat cukup tenang dan terarah saat menghadapi perubahan. Pendampingan akan lebih efektif bila "
            "diberikan penjelasan yang jelas dan kesempatan untuk memahami situasi secara bertahap. Sebagai acuan, standar adaptabilitas pada "
            "aspek Kognitif dan Afektif umumnya berada pada kisaran yang seimbang. Nilai Reflektif dan Kritis yang rendah bukan merupakan masalah, "
            "karena fungsi adaptabilitas setiap individu juga dipengaruhi oleh karakter dan kepribadian yang telah terbentuk."
        )
        
        quotient_conclusions = {
            "EQ": (
                "Menunjukkan kekuatan pada pengelolaan perasaan dan hubungan dengan lingkungan sekitar. "
                "Kepekaan emosi ini membantu individu berinteraksi dengan lebih hangat dan terbuka, serta "
                "mengekspresikan diri secara kreatif sesuai dengan situasi yang dihadapi. Kemampuan bertahan "
                "menghadapi tantangan masih memerlukan stimulasi melalui dukungan yang berkelanjutan. "
                "Pendampingan yang hangat, komunikatif, dan menenangkan akan membantu individu berkembang lebih optimal."
            ),
            "IQ": (
                "Menunjukkan kekuatan pada kemampuan berpikir secara logis, pemecahan masalah angka/pola, "
                "dan pengolahan verbal. Kematangan logika membantu Anda memahami langkah-langkah rumit secara cepat."
            ),
            "CQ": (
                "Menunjukkan kekuatan pada imajinasi, estetika, dan berpikir kreatif. Anda sangat inovatif "
                "dalam memunculkan ide-ide baru yang orisinal."
            ),
            "AQ": (
                "Menunjukkan kekuatan pada ketangguhan mental, ketahanan stres, dan tekad pantang menyerah. "
                "Anda tetap produktif dan tenang saat berada di tengah permasalahan."
            )
        }
        conclusion_quotient = quotient_conclusions.get(top_q, quotient_conclusions["EQ"])

        return HTML_TEMPLATE.format(
            participant_name=participant_name,
            intelligence_rows=intel_rows_html,
            top_intelligence_1=top_int_1,
            top_intelligence_2=top_int_2,
            disc_primary=disc_primary,
            disc_secondary=disc_secondary,
            disc_primary_desc=DISC_DESCS[disc_primary],
            disc_secondary_desc=DISC_DESCS[disc_secondary],
            left_brain_pct=left_brain_pct,
            right_brain_pct=right_brain_pct,
            dominant_brain=dominant_brain,
            brain_dominance_desc=brain_desc,
            vak_visual=vak["visual"],
            vak_auditori=vak["auditori"],
            vak_kinestetik=vak["kinestetik"],
            dominant_vak=dominant_vak,
            vak_learning_advice=vak_advice,
            iq_pct=metrics["quotients"]["IQ"],
            eq_pct=metrics["quotients"]["EQ"],
            cq_pct=metrics["quotients"]["CQ"],
            aq_pct=metrics["quotients"]["AQ"],
            top_quotient=top_q,
            top_quotient_desc=top_q_desc,
            stimulation_tips_html=stimulation_tips_html,
            adaptability_kognitif=max(adaptability["kognitif"], 1),
            adaptability_afektif=max(adaptability["afektif"], 1),
            adaptability_reflektif=max(adaptability["reflektif"], 1),
            adaptability_kritis=max(adaptability["kritis"], 1),
            adaptability_desc=adaptability_desc,
            extracurriculars_table=extracurriculars_table,
            careers_table=careers_table,
            love_language_primary=love_language_primary,
            love_language_desc=love_language_desc,
            conclusion_intelligence=conclusion_intelligence,
            conclusion_personality=conclusion_personality,
            conclusion_vak=conclusion_vak,
            conclusion_adaptability=conclusion_adaptability,
            conclusion_quotient=conclusion_quotient
        )

    @classmethod
    def generate_pdf_report(cls, participant_name: str, features_list: List[Dict[str, Any]]) -> bytes:
        """Convert calculated report HTML directly into PDF bytes using WeasyPrint or xhtml2pdf."""
        html_content = cls.generate_html_report(participant_name, features_list)
        
        # 1. Try WeasyPrint (preferred for high-fidelity flexbox support)
        if weasyprint is not None:
            try:
                pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
                return pdf_bytes
            except Exception as e:
                logger.warning(f"WeasyPrint PDF generation failed, attempting fallback: {e}")
                
        # 2. Try xhtml2pdf (pure-python fallback, doesn't require GTK)
        if pisa is not None:
            try:
                # Template already uses xhtml2pdf-safe CSS (no web fonts, no flex, no border-radius)
                pdf_buffer = io.BytesIO()
                pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
                if not pisa_status.err:
                    return pdf_buffer.getvalue()
                else:
                    logger.error(f"xhtml2pdf error: {pisa_status.err}")
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(f"xhtml2pdf PDF generation failed: {e}")
                
        # 3. Raise comprehensive import/execution error if both fail
        raise RuntimeError(
            "No HTML-to-PDF engine is available. Please install xhtml2pdf "
            "(`pip install xhtml2pdf`) or WeasyPrint (with GTK on Windows)."
        )
