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

# Load the cover fingerprint base64 dynamically
try:
    _b64_path = os.path.join(os.path.dirname(__file__), "../../original_b64.txt")
    with open(_b64_path, "r", encoding="utf-8") as _f:
        FINGERPRINT_B64 = _f.read().strip()
except Exception:
    try:
        with open("original_b64.txt", "r", encoding="utf-8") as _f:
            FINGERPRINT_B64 = _f.read().strip()
    except Exception:
        FINGERPRINT_B64 = ""

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
        
        @page cover_page {{
            size: A4;
            margin: 0;
        }}
        
        body {{
            font-family: Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #333333;
            background-color: #ffffff;
            -pdf-keep-with-next: true;
        }}
        
        .report-page {{
            width: 196mm;
            page-break-after: always;
            position: relative;
            background-color: #ffffff;
            border: 6px solid #1B365D;
        }}

        .page {{
            page: cover_page;
            position: relative;
            width: 210mm;
            height: 297mm;
            background: #ffffff;
            overflow: hidden;
            page-break-after: always;
        }}

        /* ===== Corner decorations ===== */
        /* Top-left */
        .tl-navy {{
            position: absolute; top: -60px; left: -120px;
            width: 360px; height: 300px;
            background: #1a2456;
            border-radius: 0 0 60px 0;
            transform: rotate(-12deg);
        }}
        .tl-orange {{
            position: absolute; top: 120px; left: -160px;
            width: 320px; height: 120px;
            background: #f06a1e;
            border-radius: 0 60px 60px 0;
            transform: rotate(-8deg);
        }}

        /* Top-right dot grid */
        .tr-dots {{
            position: absolute; top: 30px; right: 40px;
            width: 230px; height: 210px;
            background-image: radial-gradient(#1a2456 2.2px, transparent 2.3px);
            background-size: 16px 16px;
            -webkit-mask-image: linear-gradient(135deg, #000 35%, transparent 75%);
            mask-image: linear-gradient(135deg, #000 35%, transparent 75%);
            opacity: .85;
        }}
        .tr-lines {{
            position: absolute; top: 0; right: 0;
            width: 300px; height: 120px;
            background: repeating-linear-gradient(115deg, #1a2456 0 3px, transparent 3px 12px);
            -webkit-mask-image: linear-gradient(225deg, #000, transparent 70%);
            mask-image: linear-gradient(225deg, #000, transparent 70%);
            opacity: .25;
        }}

        /* Right edge teal accent */
        .right-teal {{
            position: absolute; top: 470px; right: -40px;
            width: 90px; height: 130px;
            background: #0f9c8e;
            border-radius: 40px 0 0 40px;
            transform: skewY(-12deg);
        }}
        .right-navy {{
            position: absolute; top: 430px; right: -20px;
            width: 40px; height: 230px;
            background: #1a2456;
            border-radius: 20px;
            transform: skewY(-12deg);
        }}

        /* Bottom-left dots */
        .bl-dots {{
            position: absolute; bottom: 90px; left: 30px;
            width: 120px; height: 150px;
            background-image: radial-gradient(#1a2456 2.2px, transparent 2.3px);
            background-size: 16px 16px;
            -webkit-mask-image: linear-gradient(45deg, #000 40%, transparent 80%);
            mask-image: linear-gradient(45deg, #000 40%, transparent 80%);
            opacity: .8;
        }}

        /* Bottom-left navy wedge */
        .bl-navy {{
            position: absolute; bottom: -120px; left: -100px;
            width: 360px; height: 320px;
            background: #1a2456;
            border-radius: 80px 0 0 0;
            transform: rotate(-12deg);
        }}
        .bl-orange {{
            position: absolute; bottom: 80px; left: -150px;
            width: 300px; height: 110px;
            background: #f06a1e;
            border-radius: 0 60px 60px 0;
            transform: rotate(8deg);
        }}

        /* Bottom-right wedges */
        .br-navy {{
            position: absolute; bottom: -100px; right: -120px;
            width: 380px; height: 300px;
            background: #1a2456;
            border-radius: 80px 0 0 0;
            transform: rotate(12deg);
        }}
        .br-orange {{
            position: absolute; bottom: 120px; right: -160px;
            width: 320px; height: 110px;
            background: #f06a1e;
            border-radius: 60px 0 0 60px;
            transform: rotate(-8deg);
        }}

        /* faint background diagonal lines mid-right */
        .mid-lines {{
            position: absolute; top: 760px; right: 0;
            width: 220px; height: 360px;
            background: repeating-linear-gradient(70deg, #e9ecf5 0 2px, transparent 2px 18px);
            opacity: .7;
        }}

        /* ===== Content ===== */
        .content {{
            position: relative;
            z-index: 5;
            text-align: center;
            padding-top: 40px;
        }}

        /* Logo */
        .logo-mark {{ margin: 0 auto 6px; }}
        .brand-name {{
            font-weight: 800;
            font-size: 52px;
            color: #f06a1e;
            line-height: .95;
            letter-spacing: -.5px;
        }}
        .brand-sub {{
            font-weight: 700;
            font-size: 30px;
            color: #1a2456;
            margin-top: 2px;
        }}
        .brand-tag {{
            font-weight: 600;
            font-size: 16px;
            color: #6b7280;
            margin-top: 6px;
            letter-spacing: .5px;
        }}

        /* Title block */
        .title-wrap {{ margin-top: 15px; }}
        .t1 {{
            font-weight: 800;
            font-size: 50px;
            color: #1a2456;
            letter-spacing: .5px;
        }}
        .t2 {{
            font-weight: 800;
            font-size: 74px;
            color: #1a2456;
            line-height: .98;
            margin-top: 2px;
            letter-spacing: .5px;
        }}
        .t3 {{
            font-weight: 700;
            font-size: 33px;
            color: #1a2456;
            margin-top: 10px;
            letter-spacing: .5px;
        }}

        .badge-row {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 18px;
            margin-top: 15px;
        }}
        .cover-badge-solid {{
            background: #1a2456;
            color: #fff;
            font-weight: 700;
            font-size: 27px;
            letter-spacing: 1px;
            padding: 12px 42px;
            border-radius: 30px;
        }}
        .badge-line {{
            height: 3px;
            width: 150px;
            background: #1a2456;
            position: relative;
        }}
        .badge-line::after {{
            content: '';
            position: absolute;
            top: 50%; transform: translateY(-50%);
            width: 13px; height: 13px;
            border-radius: 50%;
            background: #1a2456;
        }}
        .badge-line.left::after {{ right: -6px; }}
        .badge-line.right::after {{ left: -6px; }}

        /* Central infographic */
        .info {{
            position: relative;
            width: 360px; height: 306px;
            margin: 10px auto 0;
        }}
        /* dashed orbit */
        .orbit {{
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%,-50%);
            width: 276px; height: 276px;
            border: 2px dashed #c7ccdd;
            border-radius: 50%;
        }}
        /* segmented ring */
        .ring {{
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%,-50%);
            width: 192px; height: 192px;
            border-radius: 50%;
            background:
              conic-gradient(
                #f06a1e 0deg 90deg,
                #0f9c8e   90deg 180deg,
                #2a3a8c       180deg 270deg,
                #1a2456   270deg 360deg
              );
            -webkit-mask: radial-gradient(closest-side, transparent 71%, #000 72%);
            mask: radial-gradient(closest-side, transparent 71%, #000 72%);
        }}
        .ring-inner {{
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%,-50%);
            width: 150px; height: 150px;
            background: #fff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 6px 20px rgba(0,0,0,.08);
        }}
        .fingerprint {{ width: 105px; height: 105px; object-fit: contain; }}

        /* connector nodes on the ring */
        .node {{
            position: absolute;
            width: 18px; height: 18px;
            background: #fff;
            border: 3px solid #1a2456;
            border-radius: 50%;
            z-index: 4;
        }}
        .node.tl {{ top: 55px;  left: 131px; border-color: #2a3a8c; }}
        .node.tr {{ top: 55px;  right: 131px; border-color: #f06a1e; }}
        .node.bl {{ bottom: 55px; left: 131px; border-color: #2a3a8c; }}
        .node.br {{ bottom: 55px; right: 131px; border-color: #0f9c8e; }}

        /* corner feature circles */
        .feat {{
            position: absolute;
            width: 78px; height: 78px;
            background: #fff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 22px rgba(0,0,0,.12);
        }}
        .feat::before {{
            content:'';
            position:absolute;
            inset:6px;
            border-radius:50%;
            border:2px solid currentColor;
            opacity:.18;
        }}
        .feat.brain {{ top: 18px; left: 4px; color: #1a2456; }}
        .feat.brain {{ border: 4px solid #1a2456; }}
        .feat.growth {{ top: 18px; right: 4px; color: #f06a1e; border:4px solid #f06a1e;}}
        .feat.book {{ bottom: 4px; left: 34px; color: #2a3a8c; border:4px solid #2a3a8c;}}
        .feat.compass {{ bottom: 4px; right: 34px; color: #0f9c8e; border:4px solid #0f9c8e;}}
        .feat svg {{ width: 38px; height: 38px; }}

        /* Name field */
        .name-block {{
            position: absolute;
            bottom: 35px;
            left: 80px;
            right: 80px;
            z-index: 6;
        }}
        .name-label {{
            position: absolute;
            top: -18px; left: 30px;
            background: #1a2456;
            color: #fff;
            font-weight: 700;
            font-size: 15px;
            letter-spacing: 1px;
            padding: 8px 24px 8px 44px;
            border-radius: 30px;
            z-index: 2;
            display:flex; align-items:center;
        }}
        .name-label .avatar {{
            position:absolute;
            left: -2px; top: 50%;
            transform: translateY(-50%);
            width: 34px; height: 34px;
            background: #1a2456;
            border: 3px solid #fff;
            border-radius: 50%;
            display:flex; align-items:center; justify-content:center;
        }}
        .name-box {{
            border: 2px solid #e3e6ef;
            border-radius: 16px;
            height: 90px;
            background:#fff;
            display:flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 15px 30px 5px;
        }}
        .name-line {{
            width: 100%;
            border-bottom: 3px dotted #9aa1b8;
            height: 2px;
        }}
        
        .page-inner {{
            border: 2px solid #F15A24;
            margin: 4px;
            padding: 24px 34px 45px;
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
        <!-- decorations -->
        <div class="tl-navy"></div>
        <div class="tl-orange"></div>
        <div class="tr-lines"></div>
        <div class="tr-dots"></div>
        <div class="right-navy"></div>
        <div class="right-teal"></div>
        <div class="mid-lines"></div>
        <div class="bl-dots"></div>
        <div class="bl-navy"></div>
        <div class="bl-orange"></div>
        <div class="br-navy"></div>
        <div class="br-orange"></div>

        <div class="content">
          <!-- Logo mark -->
          <svg class="logo-mark" width="130" height="120" viewBox="0 0 130 120" fill="none">
            <g stroke="#f06a1e" stroke-width="9" stroke-linecap="round" fill="none">
              <path d="M20 95 V70 a45 45 0 0 1 90 0 V95"/>
              <path d="M37 95 V70 a28 28 0 0 1 56 0 V95"/>
              <path d="M54 95 V70 a11 11 0 0 1 22 0 V95"/>
            </g>
            <rect x="59" y="60" width="12" height="40" rx="6" fill="#f06a1e"/>
          </svg>

          <div class="brand-name">Tab Allia</div>
          <div class="brand-sub">Finger</div>
          <div class="brand-tag">Sentuh. Angkat. Aman.</div>

          <!-- Title -->
          <div class="title-wrap">
            <div class="t1">TES PEMETAAN</div>
            <div class="t2">POTENSI KECERDASAN</div>
            <div class="t3">KECERDASAN BERBASIS SIDIK JARI</div>
          </div>

          <div class="badge-row">
            <div class="badge-line left"></div>
            <div class="cover-badge-solid">ADVANCE REPORT</div>
            <div class="badge-line right"></div>
          </div>

          <!-- Infographic -->
          <div class="info">
            <div class="orbit"></div>
            <div class="ring"></div>
            <div class="ring-inner">
              <svg class="fingerprint" viewBox="0 0 24 24" fill="none" stroke="#1a2456" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 10a2 2 0 0 0-2 2c0 1.02-.1 2.51-.26 4" />
                <path d="M14 13.12c0 2.38 0 6.38-1 8.88" />
                <path d="M17.29 21.02c.12-.6.43-2.3.5-3.02" />
                <path d="M2 12a10 10 0 0 1 18-6" />
                <path d="M2 16h.01" />
                <path d="M21.8 16c.2-2 .131-5.354 0-6" />
                <path d="M5 19.5C5.5 18 6 15 6 12a6 6 0 0 1 .34-2" />
                <path d="M8.65 22c.21-.66.45-1.32.57-2" />
                <path d="M9 6.8a6 6 0 0 1 9 5.2v2" />
              </svg>
            </div>

            <div class="node tl"></div>
            <div class="node tr"></div>
            <div class="node bl"></div>
            <div class="node br"></div>

            <!-- Brain -->
            <div class="feat brain">
              <svg viewBox="0 0 64 64" fill="none" stroke="#1a2456" stroke-width="2.5">
                <path d="M40 14 a16 18 0 0 0 0 36 v8 a4 4 0 0 1-4 4 h-4 V12 h4 a4 4 0 0 1 4 4z" fill="#1a2456" stroke="none"/>
                <circle cx="40" cy="22" r="2.5" fill="#fff"/>
                <circle cx="48" cy="30" r="2.5" fill="#fff"/>
                <circle cx="38" cy="34" r="2.5" fill="#fff"/>
                <circle cx="46" cy="42" r="2.5" fill="#fff"/>
                <path d="M40 22 L48 30 L38 34 L46 42" stroke="#fff" stroke-width="1.5"/>
              </svg>
            </div>
            <!-- Growth -->
            <div class="feat growth">
              <svg viewBox="0 0 64 64" fill="none" stroke="#f06a1e" stroke-width="3">
                <rect x="14" y="40" width="8" height="14" fill="#f06a1e" stroke="none"/>
                <rect x="26" y="32" width="8" height="22" fill="#f06a1e" stroke="none"/>
                <rect x="38" y="24" width="8" height="30" fill="#f06a1e" stroke="none"/>
                <circle cx="30" cy="16" r="4" fill="#1a2456" stroke="none"/>
                <path d="M22 30 L30 22 L38 26 L52 12" stroke="#1a2456" stroke-width="2.5"/>
                <path d="M44 12 H52 V20" stroke="#1a2456" stroke-width="2.5"/>
              </svg>
            </div>
            <!-- Book -->
            <div class="feat book">
              <svg viewBox="0 0 64 64" fill="none" stroke="#2a3a8c" stroke-width="2.5">
                <path d="M32 18 C26 14 18 14 12 16 V46 C18 44 26 44 32 48 C38 44 46 44 52 46 V16 C46 14 38 14 32 18z" fill="#fff"/>
                <path d="M32 18 V48" />
                <circle cx="40" cy="40" r="7" fill="#fff"/>
                <line x1="45" y1="45" x2="51" y2="51" stroke-width="3"/>
              </svg>
            </div>
            <!-- Compass -->
            <div class="feat compass">
              <svg viewBox="0 0 64 64" fill="none" stroke="#0f9c8e" stroke-width="2.5">
                <circle cx="32" cy="32" r="20"/>
                <path d="M32 18 L37 32 L32 46 L27 32 Z" fill="#0f9c8e" stroke="none"/>
                <path d="M32 46 L27 32 L32 18" fill="#0c7d72" stroke="none"/>
                <circle cx="32" cy="32" r="3" fill="#fff"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- Name field -->
        <div class="name-block">
          <div class="name-label">
            <span class="avatar">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="#fff">
                <circle cx="12" cy="8" r="4"/>
                <path d="M4 21 a8 8 0 0 1 16 0 z"/>
              </svg>
            </span>
            NAMA PESERTA
          </div>
          <div class="name-box">
            <div style="width: 100%; text-align: center; font-size: 24px; font-weight: 700; color: #1a2456; margin-bottom: 8px;">{participant_name}</div>
            <div class="name-line"></div>
          </div>
        </div>
    </div>

    <!-- Page 2: MULTIPLE INTELLIGENCE -->
    <div class="report-page">
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
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">TAB ALLIA FINGER</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 2</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 3: TIPS STIMULASI KECERDASAN -->
    <div class="report-page">
        <div class="page-inner" style="padding: 30px 35px 50px;">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 10px 16px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Tips Stimulasi Kecerdasan Genetik Majemuk</td>
            </tr></table>
            <div class="participant-highlight" style="margin-bottom: 16px; font-size: 13pt;">Saran Pengembangan Potensi: <span>{participant_name}</span></div>
            
            <div style="margin-top: 10px; margin-bottom: 10px;">
                {stimulation_tips_html}
            </div>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">TAB ALLIA FINGER</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 3</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 4: BRAIN DOMINANCE & PERSONALITY TYPE (DISC) -->
    <div class="report-page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Brain Dominance & Personality Type</td>
            </tr></table>
            <div class="participant-highlight">Pola Otak & Kepribadian: <span>{participant_name}</span></div>
            
            <!-- Brain Dominance Section -->
            <div style="margin-bottom: 15px;">
                <table width="100%" style="table-layout: fixed; margin-bottom: 8px;"><tr>
                    <td bgcolor="#F4F6F9" style="padding: 5px 10px; font-size: 10pt; font-weight: bold; color: #1B365D; text-transform: uppercase; border-left: 4px solid #F15A24;">1. Dominasi Otak</td>
                </tr></table>
                <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border: 1px solid #1B365D; margin-bottom: 6px;">
                    <tr>
                        <td align="center" style="width: {left_brain_pct}%; background-color: #1B365D; color: white; padding: 8px 4px; font-size: 9pt; font-weight: bold; line-height: 14px;">OTAK KIRI {left_brain_pct}%</td>
                        <td align="center" style="width: {right_brain_pct}%; background-color: #F15A24; color: white; padding: 8px 4px; font-size: 9pt; font-weight: bold; line-height: 14px;">OTAK KANAN {right_brain_pct}%</td>
                    </tr>
                </table>
                <div style="font-size: 8.5pt; line-height: 1.35; color: #555; background-color: #fcfdfe; border: 1px solid #eef2f5; padding: 8px;">
                    <strong>Dominasi Otak {dominant_brain}:</strong> {brain_dominance_desc}
                </div>
                
                <!-- Two column details for Left and Right Brain -->
                <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-top: 8px;">
                    <tr>
                        <td width="48%" style="vertical-align: top; background-color: #F4F6F9; border-left: 3px solid #1B365D; padding: 8px 10px;">
                            <div style="font-weight: bold; color: #1B365D; font-size: 8.5pt; margin-bottom: 4px;">OTAK KIRI (LEFT BRAIN)</div>
                            <div style="font-size: 7.5pt; line-height: 1.35; color: #555;">
                                Berfokus pada logika, analisis data, berpikir sekuensial (langkah demi langkah), keteraturan, prosedur, serta penalaran angka dan verbal.
                            </div>
                        </td>
                        <td width="4%"></td>
                        <td width="48%" style="vertical-align: top; background-color: #FFF2ED; border-left: 3px solid #F15A24; padding: 8px 10px;">
                            <div style="font-weight: bold; color: #F15A24; font-size: 8.5pt; margin-bottom: 4px;">OTAK KANAN (RIGHT BRAIN)</div>
                            <div style="font-size: 7.5pt; line-height: 1.35; color: #555;">
                                Berfokus pada kreativitas, imajinasi, intuisi, ekspresi seni, pemahaman spasial, serta penyatuan gagasan secara menyeluruh (holistik).
                            </div>
                        </td>
                    </tr>
                </table>
                
                <!-- Tips to Activate both -->
                <div style="font-size: 7.5pt; line-height: 1.3; color: #444; background-color: #F4F6F9; padding: 6px 10px; margin-top: 6px; border-left: 3px solid #1B365D;">
                    <strong>Tips Aktivasi Kedua Belahan Otak:</strong> Buat daftar tugas harian, lakukan analisis data sebelum memutuskan, fokus menyelesaikan satu pekerjaan dalam satu waktu, catat gagasan di kertas, visualisasikan konsep baru, serta luangkan waktu untuk kegiatan seni kreatif secara berkala.
                </div>
            </div>
            
            <!-- DISC Section -->
            <div style="margin-top: 5px;">
                <table width="100%" style="table-layout: fixed; margin-bottom: 8px;"><tr>
                    <td bgcolor="#F4F6F9" style="padding: 5px 10px; font-size: 10pt; font-weight: bold; color: #1B365D; text-transform: uppercase; border-left: 4px solid #F15A24;">2. Tipe Kepribadian DISC</td>
                </tr></table>
                
                <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-top: 5px; margin-bottom: 5px;">
                    <tr>
                        <td width="25%" style="text-align: center; vertical-align: middle;">
                            <svg width="80" height="80" viewBox="0 0 100 100">
                                <circle cx="50" cy="50" r="45" fill="#f8f9fa" stroke="#ddd" stroke-width="1"/>
                                <path d="M50 50 L50 5 A45 45 0 0 1 95 50 Z" fill="#e53935" opacity="0.85"/>
                                <path d="M50 50 L95 50 A45 45 0 0 1 50 95 Z" fill="#ffb300" opacity="0.85"/>
                                <path d="M50 50 L50 95 A45 45 0 0 1 5 50 Z" fill="#1e88e5" opacity="0.85"/>
                                <path d="M50 50 L5 50 A45 45 0 0 1 50 5 Z" fill="#43a047" opacity="0.85"/>
                                <text x="26" y="32" font-family="Outfit" font-size="10" font-weight="bold" fill="white">D</text>
                                <text x="70" y="32" font-family="Outfit" font-size="10" font-weight="bold" fill="white">I</text>
                                <text x="70" y="72" font-family="Outfit" font-weight="bold" fill="white">S</text>
                                <text x="26" y="72" font-family="Outfit" font-weight="bold" fill="white">C</text>
                            </svg>
                        </td>
                        <td width="75%" style="vertical-align: middle; text-align: center;">
                            <table style="margin: 0 auto; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 0 12px; text-align: center;">
                                        <div style="font-size: 7.5pt; color: #666; margin-bottom: 3px; font-weight: bold;">PRIMARY TRAIT</div>
                                        <table style="margin: 0 auto; border-collapse: collapse;"><tr>
                                            <td align="center" style="background-color: #1B365D; color: white; padding: 4px 12px; font-size: 9.5pt; font-weight: bold; width: 110px; border-radius: 4px;">{disc_primary}</td>
                                        </tr></table>
                                    </td>
                                    <td style="padding: 0 12px; text-align: center;">
                                        <div style="font-size: 7.5pt; color: #666; margin-bottom: 3px; font-weight: bold;">SECONDARY TRAIT</div>
                                        <table style="margin: 0 auto; border-collapse: collapse;"><tr>
                                            <td align="center" style="background-color: #F15A24; color: white; padding: 4px 12px; font-size: 9.5pt; font-weight: bold; width: 110px; border-radius: 4px;">{disc_secondary}</td>
                                        </tr></table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
                
                <!-- Main Profiles Description -->
                <div style="font-size: 8pt; line-height: 1.35; color: #444; background-color: #F4F6F9; border-left: 3px solid #1B365D; padding: 6px 10px; margin-bottom: 8px;">
                    <strong>Karakter Utama ({disc_primary}):</strong> {disc_primary_desc}
                    <br style="margin-bottom: 3px;"/>
                    <strong>Karakter Pendukung ({disc_secondary}):</strong> {disc_secondary_desc}
                </div>
                
                <!-- Strengths and Areas of Development -->
                <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-bottom: 8px;">
                    <tr>
                        <td width="48%" style="vertical-align: top; background-color: #F4F6F9; padding: 8px 10px; border-top: 3px solid #1B365D; border-radius: 4px;">
                            <div style="font-weight: bold; color: #1B365D; font-size: 8.5pt; margin-bottom: 4px;">KEKUATAN UTAMA</div>
                            <div style="font-size: 7.5pt; line-height: 1.35; color: #555;">
                                {disc_strengths}
                            </div>
                        </td>
                        <td width="4%"></td>
                        <td width="48%" style="vertical-align: top; background-color: #FFF2ED; padding: 8px 10px; border-top: 3px solid #F15A24; border-radius: 4px;">
                            <div style="font-weight: bold; color: #F15A24; font-size: 8.5pt; margin-bottom: 4px;">AREA PENGEMBANGAN</div>
                            <div style="font-size: 7.5pt; line-height: 1.35; color: #555;">
                                {disc_develop}
                            </div>
                        </td>
                    </tr>
                </table>
                
                <!-- Situational Behavior -->
                <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-bottom: 8px; background-color: #fcfdfe; border: 1px solid #eef2f5;">
                    <tr>
                        <td width="50%" style="padding: 8px; vertical-align: top; border-right: 1px solid #eef2f5; border-bottom: 1px solid #eef2f5;">
                            <div style="font-size: 7.5pt; line-height: 1.35; color: #444;">
                                <strong>Dalam Tim:</strong> {disc_team}
                            </div>
                        </td>
                        <td width="50%" style="padding: 8px; vertical-align: top; border-bottom: 1px solid #eef2f5;">
                            <div style="font-size: 7.5pt; line-height: 1.35; color: #444;">
                                <strong>Di Bawah Tekanan:</strong> {disc_pressure}
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td width="50%" style="padding: 8px; vertical-align: top; border-right: 1px solid #eef2f5;">
                            <div style="font-size: 7.5pt; line-height: 1.35; color: #444;">
                                <strong>Saat Presentasi:</strong> {disc_presentation}
                            </div>
                        </td>
                        <td width="50%" style="padding: 8px; vertical-align: top;">
                            <div style="font-size: 7.5pt; line-height: 1.35; color: #444;">
                                <strong>Mengambil Keputusan:</strong> {disc_decision}
                            </div>
                        </td>
                    </tr>
                </table>
                
                <!-- Tips to Maximize Potential -->
                <div style="font-size: 7.5pt; line-height: 1.3; color: #444; background-color: #FFF2ED; border: 1px solid #FFD3C4; padding: 6px 10px; border-left: 4px solid #F15A24; border-radius: 4px;">
                    <strong>Tips Memaksimalkan Potensi:</strong> {disc_tips}
                </div>
            </div>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">TAB ALLIA FINGER</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 4</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 5: LEARNING STYLE (VAK) -->
    <div class="report-page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Learning Style / Gaya Belajar</td>
            </tr></table>
            <div class="participant-highlight">Kombinasi Gaya Belajar (VAK): <span>{participant_name}</span></div>
            
            <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-top: 15px; margin-bottom: 10px;">
                <tr>
                    <td width="150" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">Visual</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                             <tr>
                                 <td style="width: {vak_visual}%; background-color: #1B365D; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                 <td style="width: {vak_visual_rem}%; background-color: #F4F6F9; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                             </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{vak_visual}%</td>
                </tr>
                <tr>
                    <td width="150" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">Auditori</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                             <tr>
                                 <td style="width: {vak_auditori}%; background-color: #F15A24; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                 <td style="width: {vak_auditori_rem}%; background-color: #F4F6F9; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                             </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{vak_auditori}%</td>
                </tr>
                <tr>
                    <td width="150" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">Kinestetik</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                             <tr>
                                 <td style="width: {vak_kinestetik}%; background-color: #1B365D; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                 <td style="width: {vak_kinestetik_rem}%; background-color: #F4F6F9; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                             </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{vak_kinestetik}%</td>
                </tr>
            </table>
            
            <table width="100%" style="table-layout: fixed; margin-top: 5px;"><tr>
                <td bgcolor="#F4F6F9" style="padding: 10px 12px; font-size: 9pt; line-height: 1.4; color: #444; border-left: 4px solid #1B365D;"><strong>Saran Metode Belajar Terbimbing:</strong><br>
                Anda memiliki kecenderungan gaya belajar dominan <strong>{dominant_vak}</strong>. Untuk hasil belajar yang maksimal, disarankan untuk {vak_learning_advice}</td>
            </tr></table>
            
            <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-top: 10px; margin-bottom: 10px;">
                <tr>
                    <td width="32%" style="vertical-align: top; background-color: #F4F6F9; border-top: 3px solid #1B365D; padding: 8px; border-right: 4px solid white;">
                        <div style="font-weight: bold; color: #1B365D; font-size: 9pt; margin-bottom: 5px; text-align: center; text-transform: uppercase;">Visual</div>
                        <div style="font-size: 7.5pt; line-height: 1.35; color: #444;">
                            <strong>Ciri Khas:</strong> Mudah mengingat gambar/grafis, rapi, teratur. Sulit menyerap instruksi lisan tanpa panduan tertulis.<br/><br/>
                            <strong>Tips Belajar:</strong>
                            <ul style="margin: 0; padding-left: 12px;">
                                <li>Gunakan peta pikiran (mind map) warna-warni.</li>
                                <li>Visualisasikan materi dalam diagram/bagan.</li>
                                <li>Tandai poin penting dengan spidol penanda.</li>
                            </ul>
                        </div>
                    </td>
                    <td width="32%" style="vertical-align: top; background-color: #FFF2ED; border-top: 3px solid #F15A24; padding: 8px; border-right: 4px solid white;">
                        <div style="font-weight: bold; color: #F15A24; font-size: 9pt; margin-bottom: 5px; text-align: center; text-transform: uppercase;">Auditori</div>
                        <div style="font-size: 7.5pt; line-height: 1.35; color: #444;">
                            <strong>Ciri Khas:</strong> Mengingat penjelasan lisan dengan baik, peka terhadap nada, senang berdiskusi dan membaca nyaring.<br/><br/>
                            <strong>Tips Belajar:</strong>
                            <ul style="margin: 0; padding-left: 12px;">
                                <li>Membaca materi secara lisan atau bersuara.</li>
                                <li>Gunakan diskusi kelompok atau tanya jawab.</li>
                                <li>Rekam materi penjelasan untuk didengar ulang.</li>
                            </ul>
                        </div>
                    </td>
                    <td width="32%" style="vertical-align: top; background-color: #F4F6F9; border-top: 3px solid #1B365D; padding: 8px;">
                        <div style="font-weight: bold; color: #1B365D; font-size: 9pt; margin-bottom: 5px; text-align: center; text-transform: uppercase;">Kinestetik</div>
                        <div style="font-size: 7.5pt; line-height: 1.35; color: #444;">
                            <strong>Ciri Khas:</strong> Belajar via aktivitas fisik, menyentuh, mencoba. Sulit diam dalam waktu lama di dalam kelas.<br/><br/>
                            <strong>Tips Belajar:</strong>
                            <ul style="margin: 0; padding-left: 12px;">
                                <li>Lakukan simulasi atau praktik eksperimen.</li>
                                <li>Belajar sambil bergerak/berjalan perlahan.</li>
                                <li>Gunakan alat peraga fisik atau model nyata.</li>
                            </ul>
                        </div>
                    </td>
                </tr>
            </table>

            <table width="100%" style="table-layout: fixed; margin-top: 5px; border-collapse: collapse;">
                <tr>
                    <td bgcolor="#FFF2ED" style="padding: 10px 12px; font-size: 8.5pt; line-height: 1.4; color: #444; border-left: 4px solid #F15A24; border-top: 1px solid #FFE0B2; border-right: 1px solid #FFE0B2; border-bottom: 1px solid #FFE0B2;">
                        <span style="color: #F15A24; font-weight: bold; font-size: 9.5pt; text-transform: uppercase;">⚠️ Tantangan Belajar yang Perlu Diwaspadai</span><br/>
                        <table width="100%" style="table-layout: fixed; margin-top: 4px; border-collapse: collapse;">
                            <tr>
                                <td width="33%" style="vertical-align: top; font-size: 7.5pt; color: #555; padding-right: 8px;">
                                    <strong>Tipe Visual:</strong> Mudah terdistraksi oleh kekacauan visual atau gerakan sekitar. Sulit menyerap petunjuk lisan tanpa visual.
                                </td>
                                <td width="33%" style="vertical-align: top; font-size: 7.5pt; color: #555; padding-right: 8px;">
                                    <strong>Tipe Auditori:</strong> Rentan terganggu oleh kebisingan sekitar. Kesulitan ujian tertulis yang padat teks visual tanpa suara.
                                </td>
                                <td width="33%" style="vertical-align: top; font-size: 7.5pt; color: #555;">
                                    <strong>Tipe Kinestetik:</strong> Mudah bosan jika hanya mendengar ceramah pasif. Cenderung gelisah dalam durasi duduk belajar lama.
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">TAB ALLIA FINGER</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 5</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 6: MULTIPLE QUOTIENT -->
    <div class="report-page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Multiple Quotient / Kecerdasan Psikologis</td>
            </tr></table>
            <div class="participant-highlight">Distribusi Quotient Psikologis: <span>{participant_name}</span></div>
            
            <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-top: 15px; margin-bottom: 10px;">
                <tr>
                    <td width="150" style="font-size: 10pt; font-weight: 600; color: #333; padding: 6px 8px;">IQ (Intellectual)</td>
                    <td style="padding: 6px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                             <tr>
                                 <td style="width: {iq_pct}%; background-color: #1B365D; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                 <td style="width: {iq_pct_rem}%; background-color: #F4F6F9; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
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
                                 <td style="width: {eq_pct}%; background-color: #F15A24; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                 <td style="width: {eq_pct_rem}%; background-color: #F4F6F9; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
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
                                 <td style="width: {cq_pct}%; background-color: #1B365D; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                 <td style="width: {cq_pct_rem}%; background-color: #F4F6F9; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
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
                                 <td style="width: {aq_pct}%; background-color: #F15A24; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                 <td style="width: {aq_pct_rem}%; background-color: #F4F6F9; height: 14px; line-height: 14px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                             </tr>
                        </table>
                    </td>
                    <td width="70" style="font-size: 11pt; font-weight: 700; color: #1B365D; text-align: right; padding: 6px 8px;">{aq_pct}%</td>
                </tr>
            </table>
            
            <table width="100%" style="table-layout: fixed; margin-top: 5px;"><tr>
                <td bgcolor="#F4F6F9" style="padding: 10px 12px; font-size: 9pt; line-height: 1.4; color: #444; border-left: 4px solid #1B365D;"><strong>Keseimbangan Aspek Psikologis:</strong><br>
                Quotient tertinggi Anda berada pada <strong>{top_quotient}</strong>. Ini menandakan kemampuan yang sangat baik dalam {top_quotient_desc}.</td>
            </tr></table>

            <!-- 2x2 Grid defining IQ, EQ, CQ, AQ -->
            <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-top: 10px; margin-bottom: 10px;">
                <tr>
                    <td width="48%" style="vertical-align: top; background-color: #F4F6F9; border-left: 3px solid #1B365D; padding: 8px 10px; border-bottom: 8px solid white;">
                        <div style="font-weight: bold; color: #1B365D; font-size: 8.5pt; margin-bottom: 4px;">INTELLIGENCE QUOTIENT (IQ)</div>
                        <div style="font-size: 7.5pt; line-height: 1.35; color: #555;">
                            Mengukur kemampuan pemecahan masalah secara logis, analisis pola/angka, dan penalaran akademis verbal. Membantu memahami konsep rumit secara runut.
                        </div>
                    </td>
                    <td width="4%"></td>
                    <td width="48%" style="vertical-align: top; background-color: #FFF2ED; border-left: 3px solid #F15A24; padding: 8px 10px; border-bottom: 8px solid white;">
                        <div style="font-weight: bold; color: #F15A24; font-size: 8.5pt; margin-bottom: 4px;">EMOTIONAL QUOTIENT (EQ)</div>
                        <div style="font-size: 7.5pt; line-height: 1.35; color: #555;">
                            Mengukur kecerdasan emosional, empati sosial, kesadaran diri, motivasi diri, serta kepekaan hubungan interpersonal dengan lingkungan sosial.
                        </div>
                    </td>
                </tr>
                <tr>
                    <td width="48%" style="vertical-align: top; background-color: #FFF2ED; border-left: 3px solid #F15A24; padding: 8px 10px;">
                        <div style="font-weight: bold; color: #F15A24; font-size: 8.5pt; margin-bottom: 4px;">CREATIVITY QUOTIENT (CQ)</div>
                        <div style="font-size: 7.5pt; line-height: 1.35; color: #555;">
                            Mengukur orisinalitas berpikir, kemampuan melahirkan solusi alternatif baru (out-of-the-box), imajinasi kreatif, dan dorongan inovasi.
                        </div>
                    </td>
                    <td width="4%"></td>
                    <td width="48%" style="vertical-align: top; background-color: #F4F6F9; border-left: 3px solid #1B365D; padding: 8px 10px;">
                        <div style="font-weight: bold; color: #1B365D; font-size: 8.5pt; margin-bottom: 4px;">ADVERSITY QUOTIENT (AQ)</div>
                        <div style="font-size: 7.5pt; line-height: 1.35; color: #555;">
                            Mengukur daya juang, ketangguhan mental, daya tahan terhadap stres, serta kemampuan untuk bangkit kembali di kala menghadapi hambatan.
                        </div>
                    </td>
                </tr>
            </table>

            <!-- AQ Stimulation Box -->
            <table width="100%" style="table-layout: fixed; margin-top: 5px; border-collapse: collapse;">
                <tr>
                    <td bgcolor="#F4F6F9" style="padding: 10px 12px; font-size: 8.5pt; line-height: 1.4; color: #444; border-left: 4px solid #1B365D; border-top: 1px solid #E1E7E5; border-right: 1px solid #E1E7E5; border-bottom: 1px solid #E1E7E5;">
                        <span style="color: #1B365D; font-weight: bold; font-size: 9.5pt; text-transform: uppercase;">💪 Langkah Penguatan & Stimulasi Ketahanan (AQ)</span><br/>
                        <div style="font-size: 7.5pt; line-height: 1.35; color: #555; margin-top: 4px;">
                            Adversity Quotient (AQ) merupakan penentu utama keberhasilan dalam menghadapi masa-aspek sulit. Latihlah stimulasi berikut untuk meningkatkan ketangguhan Anda:
                            <ul style="margin: 3px 0 0 0; padding-left: 12px;">
                                <li><strong>Reframing Masalah:</strong> Pandanglah masalah bukan sebagai kegagalan permanen, melainkan sebagai tantangan sementara yang bisa diselesaikan secara bertahap.</li>
                                <li><strong>Meningkatkan Kontrol Diri:</strong> Fokuslah pada hal-hal yang dapat diubah dan dipengaruhi langsung oleh usaha Anda, daripada memikirkan hal di luar kendali.</li>
                                <li><strong>Mengambil Tanggung Jawab:</strong> Cari solusi aktif alih-alih menyalahkan keadaan atau orang lain ketika situasi tidak berjalan sesuai rencana.</li>
                            </ul>
                        </div>
                    </td>
                </tr>
            </table>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">TAB ALLIA FINGER</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 6</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 7: ADAPTABILITAS KEPRIBADIAN -->
    <div class="report-page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Adaptabilitas Kepribadian</td>
            </tr></table>
            <div class="participant-highlight">Pola Adaptabilitas Kepribadian: <span>{participant_name}</span></div>
            
            <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-top: 18px; margin-bottom: 15px;">
                <tr>
                    <td width="160" style="font-size: 11.5pt; font-weight: 600; color: #333; padding: 8px 10px;">SELF KOGNITIF</td>
                    <td style="padding: 8px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                             <tr>
                                 <td style="width: {adaptability_kognitif}%; background-color: #1B365D; height: 18px; line-height: 18px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                 <td style="width: {adaptability_kognitif_rem}%; background-color: #F4F6F9; height: 18px; line-height: 18px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                             </tr>
                        </table>
                    </td>
                    <td width="80" style="font-size: 13pt; font-weight: 700; color: #1B365D; text-align: right; padding: 8px 10px;">{adaptability_kognitif}%</td>
                </tr>
                <tr>
                    <td width="160" style="font-size: 11.5pt; font-weight: 600; color: #333; padding: 8px 10px;">AFEKTIF</td>
                    <td style="padding: 8px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                             <tr>
                                 <td style="width: {adaptability_afektif}%; background-color: #F15A24; height: 18px; line-height: 18px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                 <td style="width: {adaptability_afektif_rem}%; background-color: #F4F6F9; height: 18px; line-height: 18px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                             </tr>
                        </table>
                    </td>
                    <td width="80" style="font-size: 13pt; font-weight: 700; color: #1B365D; text-align: right; padding: 8px 10px;">{adaptability_afektif}%</td>
                </tr>
                <tr>
                    <td width="160" style="font-size: 11.5pt; font-weight: 600; color: #333; padding: 8px 10px;">REFLEKTIF</td>
                    <td style="padding: 8px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                             <tr>
                                 <td style="width: {adaptability_reflektif}%; background-color: #1B365D; height: 18px; line-height: 18px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                 <td style="width: {adaptability_reflektif_rem}%; background-color: #F4F6F9; height: 18px; line-height: 18px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                             </tr>
                        </table>
                    </td>
                    <td width="80" style="font-size: 13pt; font-weight: 700; color: #1B365D; text-align: right; padding: 8px 10px;">{adaptability_reflektif}%</td>
                </tr>
                <tr>
                    <td width="160" style="font-size: 11.5pt; font-weight: 600; color: #333; padding: 8px 10px;">KRITIS</td>
                    <td style="padding: 8px 5px; vertical-align: middle;">
                        <table width="100%" cellspacing="0" cellpadding="0" style="table-layout: fixed; border-collapse: collapse; line-height: 0; font-size: 0;">
                             <tr>
                                 <td style="width: {adaptability_kritis}%; background-color: #F15A24; height: 18px; line-height: 18px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                                 <td style="width: {adaptability_kritis_rem}%; background-color: #F4F6F9; height: 18px; line-height: 18px; font-size: 1px; padding: 0; border: none;">&nbsp;</td>
                             </tr>
                        </table>
                    </td>
                    <td width="80" style="font-size: 13pt; font-weight: 700; color: #1B365D; text-align: right; padding: 8px 10px;">{adaptability_kritis}%</td>
                </tr>
            </table>
            
            <table width="100%" style="table-layout: fixed; margin-top: 10px; margin-bottom: 12px;"><tr>
                <td bgcolor="#F4F6F9" style="padding: 14px 16px; font-size: 10.5pt; line-height: 1.5; color: #333333; border-left: 4px solid #1B365D;"><strong>Gaya Penyesuaian Diri Utama:</strong><br>
                {adaptability_desc}
                <br style="margin-bottom: 6px;"/>
                <em style="color: #666666;">Catatan: Nilai Reflektif dan Kritis yang rendah merupakan hal wajar dan bukan masalah, karena fungsi adaptabilitas dipengaruhi oleh karakter dan kematangan kepribadian yang telah terbentuk.</em></td>
            </tr></table>

            <!-- 2x2 Grid defining 4 Adaptability Modes -->
            <table width="100%" style="table-layout: fixed; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px;">
                <tr>
                    <td width="48%" style="vertical-align: top; background-color: #F4F6F9; border-left: 4px solid #1B365D; padding: 12px 14px; border-bottom: 12px solid white;">
                        <div style="font-weight: bold; color: #1B365D; font-size: 11pt; margin-bottom: 6px;">SELF KOGNITIF</div>
                        <div style="font-size: 9.5pt; line-height: 1.5; color: #333333;">
                            Menyesuaikan diri melalui pemahaman rasional, analisis logika, dan penalaran fakta objektif. Cepat menguasai aturan dan skema kerja yang baru.
                        </div>
                    </td>
                    <td width="4%"></td>
                    <td width="48%" style="vertical-align: top; background-color: #FFF2ED; border-left: 4px solid #F15A24; padding: 12px 14px; border-bottom: 12px solid white;">
                        <div style="font-weight: bold; color: #F15A24; font-size: 11pt; margin-bottom: 6px;">AFEKTIF (EMOSIONAL)</div>
                        <div style="font-size: 9.5pt; line-height: 1.5; color: #333333;">
                            Menyesuaikan diri lewat keselarasan emosi, empati sosial, dan menjaga kehangatan hubungan. Peka terhadap kenyamanan perasaan kelompok.
                        </div>
                    </td>
                </tr>
                <tr>
                    <td width="48%" style="vertical-align: top; background-color: #FFF2ED; border-left: 4px solid #F15A24; padding: 12px 14px;">
                        <div style="font-weight: bold; color: #F15A24; font-size: 11pt; margin-bottom: 6px;">REFLEKTIF</div>
                        <div style="font-size: 9.5pt; line-height: 1.5; color: #333333;">
                            Menyesuaikan diri dengan mengamati keadaan, berkaca pada pengalaman masa lalu, dan merenungkan respons terbaik secara tenang.
                        </div>
                    </td>
                    <td width="4%"></td>
                    <td width="48%" style="vertical-align: top; background-color: #F4F6F9; border-left: 4px solid #1B365D; padding: 12px 14px;">
                        <div style="font-weight: bold; color: #1B365D; font-size: 11pt; margin-bottom: 6px;">KRITIS</div>
                        <div style="font-size: 9.5pt; line-height: 1.5; color: #333333;">
                            Menyesuaikan diri dengan mengevaluasi secara kritis, mempertanyakan asumsi dasar, dan mencari tahu kebenaran sistemik di balik perubahan.
                        </div>
                    </td>
                </tr>
            </table>

            <!-- Adaptability Advice Box -->
            <table width="100%" style="table-layout: fixed; margin-top: 10px; border-collapse: collapse;">
                <tr>
                    <td bgcolor="#FFF2ED" style="padding: 14px 16px; font-size: 10.5pt; line-height: 1.5; color: #333333; border-left: 4px solid #F15A24; border-top: 1px solid #FFE0B2; border-right: 1px solid #FFE0B2; border-bottom: 1px solid #FFE0B2;">
                        <span style="color: #F15A24; font-weight: bold; font-size: 12pt; text-transform: uppercase;">💡 Area Pengembangan Adaptabilitas</span><br/>
                        <div style="font-size: 9.5pt; line-height: 1.5; color: #333333; margin-top: 6px;">
                            Untuk mengoptimalkan cara Anda menyesuaikan diri terhadap tantangan baru, latihlah aspek-aspek berikut secara bertahap:
                            <ul style="margin: 6px 0 0 0; padding-left: 14px; line-height: 1.6;">
                                <li><strong>Keluwesan Emosi (Afektif):</strong> Latihlah ketenangan emosi ketika menghadapi perubahan mendadak yang tidak sejalan dengan rencana.</li>
                                <li><strong>Membuka Diri:</strong> Cobalah mendengarkan sudut pandang alternatif dengan sikap terbuka sebelum memberikan penolakan kognitif.</li>
                                <li><strong>Refleksi & Aksi:</strong> Gabungkan pemikiran mendalam (Reflektif) dengan aksi nyata agar tidak terjebak dalam lingkaran overthinking.</li>
                            </ul>
                        </div>
                    </td>
                </tr>
            </table>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">TAB ALLIA FINGER</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 7</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 8: REFERENSI EKSTRAKURIKULER & LOVE LANGUAGE -->
    <div class="report-page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Referensi Ekstrakurikuler & Love Language</td>
            </tr></table>
            <div class="participant-highlight">Aktivitas Tambahan & Bahasa Cinta: <span>{participant_name}</span></div>
            
            <!-- Extracurriculars Table -->
            <div>
                <table width="100%" style="table-layout: fixed; margin-bottom: 12px;"><tr>
                    <td bgcolor="#F4F6F9" style="padding: 6px 12px; font-size: 11pt; font-weight: bold; color: #1B365D; text-transform: uppercase; border-left: 4px solid #F15A24;">1. Pilihan Ekstrakurikuler</td>
                </tr></table>
                {extracurriculars_table}
                <div style="font-size: 9.5pt; color: #666; margin-top: 8px; text-align: center;">
                    Urutan 1-6: Sangat Direkomendasikan | 7-11: Cukup Direkomendasikan | 12-16: Kurang Direkomendasikan
                </div>
            </div>
            
            <!-- Love Language Section -->
            <div style="margin-top: 15px;">
                <table width="100%" style="table-layout: fixed; margin-bottom: 12px;"><tr>
                    <td bgcolor="#F4F6F9" style="padding: 6px 12px; font-size: 11pt; font-weight: bold; color: #1B365D; text-transform: uppercase; border-left: 4px solid #F15A24;">2. Love Language (Bahasa Cinta)</td>
                </tr></table>
                
                <table width="100%" style="table-layout: fixed; margin-top: 15px;"><tr>
                    <td bgcolor="#F4F6F9" style="padding: 14px 16px; font-size: 10.5pt; line-height: 1.5; color: #333333; border-left: 4px solid #1B365D;"><strong>Bahasa Cinta Dominan ({love_language_primary}):</strong><br>
                    {love_language_desc}
                    <br style="margin-bottom: 6px;"/>
                    <em style="color: #666666;">Tips: Cinta = Usaha Kecil Tapi Konsisten. Tenang dan teliti. Merasa disayang bila dibantu dengan tertib dan diperhatikan kebutuhannya. 👉 Tidak perlu berlebihan, yang penting konsisten.</em></td>
                </tr></table>
            </div>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">TAB ALLIA FINGER</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 8</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 9: REFERENSI AKADEMIK & KARIR -->
    <div class="report-page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Referensi Akademik & Karir</td>
            </tr></table>
            <div class="participant-highlight">Bidang Studi & Profesi Pilihan: <span>{participant_name}</span></div>
            
            <div style="margin-top: 10px;">
                {careers_table}
                <div style="font-size: 9.5pt; color: #666; margin-top: 12px; text-align: center;">
                    Urutan 1-20: Sangat Direkomendasikan | 21-40: Cukup Direkomendasikan | 41-60: Kurang Direkomendasikan
                </div>
            </div>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">TAB ALLIA FINGER</td>
                    <td width="50%" style="text-align: right; color: #888;">Halaman 9</td>
                </tr></table>
            </div>
        </div>
    </div>

    <!-- Page 10: KESIMPULAN & SARAN -->
    <div class="report-page">
        <div class="page-inner">
            <table width="100%" style="table-layout: fixed; margin-bottom: 15px;"><tr>
                <td bgcolor="#1B365D" style="padding: 8px 12px; color: #FFFFFF; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Kesimpulan & Saran Pengembangan</td>
            </tr></table>
            <div class="participant-highlight">Kesimpulan Hasil Evaluasi: <span>{participant_name}</span></div>
            
            <div style="font-size: 10pt; line-height: 1.55; color: #333333; overflow: hidden; display: block; margin-top: 12px;">
                <div style="margin-bottom: 12px; padding-bottom: 4px;">
                    <strong>Multiple Intelligence:</strong> {conclusion_intelligence}
                </div>
                <hr style="border: none; height: 1px; background-color: #F15A24; margin: 10px 0;">
                <div style="margin-bottom: 12px; padding-bottom: 4px;">
                    <strong>Tipe Kepribadian DISC:</strong> {conclusion_personality}
                </div>
                <hr style="border: none; height: 1px; background-color: #F15A24; margin: 10px 0;">
                <div style="margin-bottom: 12px; padding-bottom: 4px;">
                    <strong>Bahasa Cinta (Love Language):</strong> {love_language_desc}
                </div>
                <hr style="border: none; height: 1px; background-color: #F15A24; margin: 10px 0;">
                <div style="margin-bottom: 12px; padding-bottom: 4px;">
                    <strong>Brain Dominance & Gaya Belajar:</strong> Dominasi {dominant_brain} Brain ({left_brain_pct}% kiri vs {right_brain_pct}% kanan) menunjukkan kecenderungan cara berpikir {dominant_brain}. {conclusion_vak}
                </div>
                <hr style="border: none; height: 1px; background-color: #F15A24; margin: 10px 0;">
                <div style="margin-bottom: 12px; padding-bottom: 4px;">
                    <strong>Adaptabilitas & Kecerdasan Psikologis:</strong> {conclusion_adaptability} {conclusion_quotient}
                </div>
            </div>
            
            <div class="page-footer">
                <hr style="border: none; height: 1px; background-color: #F15A24; margin-bottom: 5px;">
                <table width="100%" style="table-layout: fixed; width: 100%;"><tr>
                    <td width="50%" style="text-align: left; color: #1B365D; font-weight: bold;">TAB ALLIA FINGER</td>
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
        # Occipital lobe (Visual) = Left/Right Pinky
        visual_raw = finger_weights["left_pinky"] + finger_weights["right_pinky"]
        # Temporal lobe (Auditory) = Left/Right Ring
        auditori_raw = finger_weights["left_ring"] + finger_weights["right_ring"]
        # Parietal lobe (Kinesthetic) = Left/Right Middle
        kinestetik_raw = finger_weights["left_middle"] + finger_weights["right_middle"]
        
        # Add intelligence-based scaling for VAK to align with the core talents
        visual_raw += (intel_pcts["visual-spasial"] + intel_pcts["naturalis"]) * 0.5
        auditori_raw += (intel_pcts["linguistik"] + intel_pcts["musikal"]) * 0.5
        kinestetik_raw += intel_pcts["kinestetik"] * 1.0
        
        total_vak = visual_raw + auditori_raw + kinestetik_raw
        vak_pcts = {
            "visual": round((visual_raw / total_vak) * 100, 2),
            "auditori": round((auditori_raw / total_vak) * 100, 2),
            "kinestetik": round((kinestetik_raw / total_vak) * 100, 2)
        }
        
        # Map patterns from features_list
        patterns = {
            "left_thumb": "loop", "left_index": "loop", "left_middle": "loop", "left_ring": "loop", "left_pinky": "loop",
            "right_thumb": "loop", "right_index": "loop", "right_middle": "loop", "right_ring": "loop", "right_pinky": "loop"
        }
        for f in features_list:
            pos = f.get("finger_position")
            pt = f.get("pattern_type")
            if pos in patterns and pt:
                patterns[pos] = pt.lower()

        # 5. DISC mapping based on fingerprint patterns and Multiple Intelligence percentages
        d_pattern_bonus = 0.0
        if patterns["right_thumb"] in ["whorl", "composite"]: d_pattern_bonus += 25.0
        if patterns["left_thumb"] in ["whorl", "composite"]: d_pattern_bonus += 15.0
        if patterns["right_index"] in ["whorl", "composite"]: d_pattern_bonus += 10.0
        
        i_pattern_bonus = 0.0
        if patterns["left_thumb"] == "loop": i_pattern_bonus += 25.0
        if patterns["right_thumb"] == "loop": i_pattern_bonus += 15.0
        if patterns["left_index"] == "loop": i_pattern_bonus += 10.0
        
        s_pattern_bonus = 0.0
        if patterns["left_thumb"] == "loop": s_pattern_bonus += 20.0
        if patterns["right_thumb"] == "loop": s_pattern_bonus += 20.0
        if patterns["left_middle"] == "loop" or patterns["right_middle"] == "loop": s_pattern_bonus += 10.0
        
        c_pattern_bonus = 0.0
        for finger in ["left_thumb", "right_thumb", "left_index", "right_index"]:
            if patterns[finger] in ["arch", "tented_arch"]:
                c_pattern_bonus += 25.0
        if patterns["right_index"] in ["whorl", "composite"]: c_pattern_bonus += 10.0
        if patterns["left_index"] in ["whorl", "composite"]: c_pattern_bonus += 10.0

        d_score = (1.5 * intel_pcts["intrapersonal"]) + (1.0 * intel_pcts["logical"]) + d_pattern_bonus
        i_score = (1.5 * intel_pcts["interpersonal"]) + (1.0 * intel_pcts["linguistik"]) + i_pattern_bonus
        s_score = (1.0 * intel_pcts["interpersonal"]) + (1.2 * intel_pcts["musikal"]) + (0.8 * intel_pcts["kinestetik"]) + s_pattern_bonus
        c_score = (2.0 * intel_pcts["logical"]) + (1.2 * intel_pcts["visual-spasial"]) + c_pattern_bonus

        total_disc = d_score + i_score + s_score + c_score
        disc_pcts = {
            "Dominan": round((d_score / total_disc) * 100, 2),
            "Influential": round((i_score / total_disc) * 100, 2),
            "Steady": round((s_score / total_disc) * 100, 2),
            "Compliant": round((c_score / total_disc) * 100, 2)
        }
        
        # 6. Love Languages mapping based on DISC and Multiple Intelligences
        acts_of_service = (0.4 * disc_pcts["Compliant"]) + (0.4 * disc_pcts["Dominan"]) + (intel_pcts["kinestetik"] + intel_pcts["logical"]) * 0.5
        words_of_affirmation = (0.4 * disc_pcts["Influential"]) + (0.3 * disc_pcts["Dominan"]) + intel_pcts["linguistik"] * 1.5
        quality_time = (0.5 * disc_pcts["Steady"]) + intel_pcts["interpersonal"] * 1.0
        receiving_gifts = (0.5 * disc_pcts["Compliant"]) + intel_pcts["visual-spasial"] * 1.0
        physical_touch = (0.4 * disc_pcts["Steady"]) + intel_pcts["kinestetik"] * 1.5
        
        total_ll = acts_of_service + words_of_affirmation + quality_time + receiving_gifts + physical_touch
        ll_pcts = {
            "Acts of Service": round((acts_of_service / total_ll) * 100, 2),
            "Words of Affirmation": round((words_of_affirmation / total_ll) * 100, 2),
            "Quality Time": round((quality_time / total_ll) * 100, 2),
            "Receiving Gifts": round((receiving_gifts / total_ll) * 100, 2),
            "Physical Touch": round((physical_touch / total_ll) * 100, 2)
        }

        # 7. Adaptability (Kognitif, Afektif, Reflektif, Kritis)
        adaptability_pcts = {
            "kognitif": disc_pcts["Compliant"],
            "afektif": disc_pcts["Influential"],
            "reflektif": disc_pcts["Steady"],
            "kritis": disc_pcts["Dominan"]
        }
        
        return {
            "intelligences": intel_pcts,
            "quotients": q_pcts,
            "brain": brain_pcts,
            "vak": vak_pcts,
            "adaptability": adaptability_pcts,
            "disc": disc_pcts,
            "love_languages": ll_pcts
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
        stimulation_tips_html = '<table width="100%" style="table-layout: fixed; border-collapse: separate; border-spacing: 16px 20px;">\n'
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
    <td width="50%" style="vertical-align: top; padding-bottom: 18px;">
      <div style="border-left: 4px solid {border_color1}; padding-left: 12px;">
        <div style="font-size: 12pt; font-weight: bold; color: {label_color1}; margin-bottom: 6px;">{display_name1}</div>
        <div style="font-size: 10.5pt; line-height: 1.5; color: #333333;">{tips1}</div>
      </div>
    </td>
    <td width="50%" style="vertical-align: top; padding-bottom: 18px;">
      <div style="border-left: 4px solid {border_color2}; padding-left: 12px;">
        <div style="font-size: 12pt; font-weight: bold; color: {label_color2}; margin-bottom: 6px;">{display_name2}</div>
        <div style="font-size: 10.5pt; line-height: 1.5; color: #333333;">{tips2}</div>
      </div>
    </td>
  </tr>\n"""
        stimulation_tips_html += "</table>"
            
        # DISC mapping from calculated metrics
        disc_pcts = metrics["disc"]
        sorted_disc = sorted(disc_pcts.items(), key=lambda x: x[1], reverse=True)
        disc_primary = sorted_disc[0][0]
        disc_secondary = sorted_disc[1][0]
        
        # Rich profiles from more_content.md
        DISC_PROFILES = {
            "Dominan": {
                "desc": "Individu yang tegas, mandiri, berani mengambil keputusan, dan berorientasi kuat pada hasil. Cepat bertindak dan menyukai tantangan baru.",
                "strengths": "Tegas dan mandiri dalam bertindak, berorientasi kuat pada hasil akhir, memiliki keberanian mengambil keputusan cepat, serta menyukai tantangan baru.",
                "develop": "Perlu belajar mendengarkan masukan orang lain sebelum memutuskan, meningkatkan kesabaran terhadap proses, serta lebih peka terhadap perasaan rekan tim.",
                "team": "Mendorong tim untuk fokus pada target dan menyelesaikan pekerjaan secara cepat.",
                "presentation": "Menyampaikan poin utama secara langsung (to the point) dan penuh percaya diri.",
                "pressure": "Tetap fokus pada hasil akhir, namun rentan menjadi kurang sabar atau menuntut.",
                "decision": "Mengambil keputusan secara mandiri dan cepat, terkadang tanpa data yang lengkap.",
                "tips": "Gunakan ketegasan Anda untuk memimpin dan menyelesaikan hambatan. Latihlah untuk mendengarkan masukan orang lain dan imbangi ketegasan dengan empati."
            },
            "Influential": {
                "desc": "Individu yang ramah, komunikatif, ekspresif, antusias, mudah bergaul, dan menyukai interaksi sosial serta membangun suasana yang menyenangkan.",
                "strengths": "Komunikatif dalam berinteraksi, ekspresif dan antusias, mudah beradaptasi di lingkungan sosial baru, serta kreatif dan penuh dengan ide-ide segar.",
                "develop": "Perlu meningkatkan kedisiplinan terhadap waktu dan detail, fokus menyelesaikan satu tugas sebelum memulai tugas lain, serta mengurangi sifat impulsif.",
                "team": "Membangun atmosfer kerja yang ceria, penuh kolaborasi, dan memotivasi rekan tim.",
                "presentation": "Sangat dinamis, komunikatif, menarik perhatian audiens, dan menggunakan ekspresi yang hidup.",
                "pressure": "Cenderung berusaha menjaga hubungan baik dan mencairkan suasana agar tetap positif.",
                "decision": "Mengambil keputusan secara cepat berdasarkan intuisi, perasaan, atau masukan sosial.",
                "tips": "Gunakan kemampuan komunikasi Anda untuk membangun relasi. Fokuslah menyelesaikan tugas yang telah dimulai, dan buatlah perencanaan tertulis agar tidak mudah teralihkan."
            },
            "Steady": {
                "desc": "Individu yang tenang, sabar, kooperatif, konsisten, menyukai stabilitas, dan berusaha menjaga keharmonisan hubungan serta menghindari konflik.",
                "strengths": "Sabar dan menjadi pendengar yang sangat baik, kooperatif dalam kelompok, konsisten dalam bekerja, serta menjaga stabilitas dan harmoni.",
                "develop": "Perlu belajar menghadapi perubahan mendadak dengan lebih fleksibel, berani mengutarakan pendapat/ketidaksetujuan, serta mengambil inisiatif mandiri.",
                "team": "Menjadi perekat hubungan dalam tim dan mendukung kerja sama secara damai.",
                "presentation": "Menyampaikan informasi secara tenang, sistematis, dan lebih suka dalam kelompok kecil.",
                "pressure": "Cenderung memendam kecemasan demi menjaga kedamaian di sekitarnya.",
                "decision": "Membutuhkan waktu untuk berdiskusi, mempertimbangkan dampak sosial, dan mencari konsensus.",
                "tips": "Gunakan loyalitas dan kesabaran Anda untuk mendukung tim. Latihlah keberanian untuk mengutarakan ketidaksetujuan secara asertif dan cobalah keluar dari zona nyaman."
            },
            "Compliant": {
                "desc": "Individu yang analitis, teliti, berhati-hati, terstruktur, rapi, bertanggung jawab, dan sangat memperhatikan aturan atau prosedur.",
                "strengths": "Teliti dan sangat sistematis dalam bekerja, analitis dan logis, nyaman dengan keteraturan/prosedur yang jelas, serta bertanggung jawab menjaga kualitas kerja.",
                "develop": "Perlu mengurangi sifat perfeksionisme/overthinking, lebih fleksibel menghadapi perubahan mendadak, serta berani mengambil keputusan lebih cepat.",
                "team": "Membantu memastikan seluruh pekerjaan berjalan rapi, akurat, dan sesuai dengan aturan.",
                "presentation": "Menyampaikan data secara rinci, akurat, terstruktur, dan didukung fakta yang kuat.",
                "pressure": "Tetap fokus pada detail pekerjaan, namun rentan mengalami kecemasan atau kekhawatiran berlebih.",
                "decision": "Memerlukan pertimbangan yang matang, data yang lengkap, dan analisis risiko sebelum memutuskan.",
                "tips": "Gunakan ketelitian Anda untuk menghasilkan karya berkualitas tinggi. Latihlah keluwesan untuk menerima perubahan tak terduga, dan belajarlah memutuskan sesuatu meskipun keadaannya belum sempurna."
            }
        }
        
        p_profile = DISC_PROFILES[disc_primary]
        disc_primary_desc = p_profile['desc']
        disc_strengths = p_profile['strengths']
        disc_develop = p_profile['develop']
        disc_team = p_profile['team']
        disc_presentation = p_profile['presentation']
        disc_pressure = p_profile['pressure']
        disc_decision = p_profile['decision']
        disc_tips = p_profile['tips']
        
        s_profile = DISC_PROFILES[disc_secondary]
        disc_secondary_desc = s_profile['desc']
            
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
        
        vak_visual_pct = max(vak.get("visual", 0), 1)
        vak_auditori_pct = max(vak.get("auditori", 0), 1)
        vak_kinestetik_pct = max(vak.get("kinestetik", 0), 1)
        vak_visual_rem = max(100 - vak_visual_pct, 1)
        vak_auditori_rem = max(100 - vak_auditori_pct, 1)
        vak_kinestetik_rem = max(100 - vak_kinestetik_pct, 1)
        
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
        
        # Quotients remaining percentages
        iq_pct = max(metrics["quotients"].get("IQ", 0), 1)
        eq_pct = max(metrics["quotients"].get("EQ", 0), 1)
        cq_pct = max(metrics["quotients"].get("CQ", 0), 1)
        aq_pct = max(metrics["quotients"].get("AQ", 0), 1)
        iq_pct_rem = max(100 - iq_pct, 1)
        eq_pct_rem = max(100 - eq_pct, 1)
        cq_pct_rem = max(100 - cq_pct, 1)
        aq_pct_rem = max(100 - aq_pct, 1)
        
        # Adaptability details
        adaptability = metrics["adaptability"]
        adaptability_desc = (
            "Cenderung menyesuaikan diri dengan cara memahami situasi yang dihadapi. "
            "Ia berusaha menangkap maksud dan kondisi terlebih dahulu sebelum merespons, "
            "sehingga terlihat cukup tenang dan terarah saat menghadapi perubahan. "
            "Pendampingan akan lebih efektif bila diberikan penjelasan yang jelas "
            "dan kesempatan untuk memahami situasi secara bertahap."
        )
        
        # Adaptability remaining percentages
        adaptability_kognitif = max(adaptability.get("kognitif", 0), 1)
        adaptability_afektif = max(adaptability.get("afektif", 0), 1)
        adaptability_reflektif = max(adaptability.get("reflektif", 0), 1)
        adaptability_kritis = max(adaptability.get("kritis", 0), 1)
        adaptability_kognitif_rem = max(100 - adaptability_kognitif, 1)
        adaptability_afektif_rem = max(100 - adaptability_afektif, 1)
        adaptability_reflektif_rem = max(100 - adaptability_reflektif, 1)
        adaptability_kritis_rem = max(100 - adaptability_kritis, 1)
        
        # Love Language mapping based on calculated metrics
        love_languages = metrics["love_languages"]
        sorted_ll = sorted(love_languages.items(), key=lambda x: x[1], reverse=True)
        love_language_primary = sorted_ll[0][0]
        
        love_language_desc = LOVE_LANGUAGE_DESCS.get(love_language_primary, {}).get("desc", "")
        love_language_title = LOVE_LANGUAGE_DESCS.get(love_language_primary, {}).get("title", love_language_primary)
        
        love_language_tips_map = {
            "Acts of Service": "Berikan bantuan spesifik pada tugas atau kebutuhannya tanpa perlu menunggu diminta. Dukungan melalui tindakan nyata yang solutif sangat berharga baginya.",
            "Words of Affirmation": "Sampaikan pujian tulus atas usaha dan pencapaiannya. Kata-kata penyemangat, pengakuan atas kompetensinya, dan apresiasi verbal sangat berarti.",
            "Quality Time": "Sediakan waktu khusus untuk mengobrol secara mendalam, mendengarkan keluh kesahnya, dan beraktivitas bersama tanpa distraksi gawai atau pekerjaan.",
            "Receiving Gifts": "Berikan hadiah kecil atau kejutan yang bermakna sebagai simbol perhatian. Pemberian yang tulus menunjukkan bahwa Anda memikirkan dan peduli padanya.",
            "Physical Touch": "Tunjukkan dukungan emosional melalui sentuhan fisik yang menenangkan seperti pelukan hangat, rangkulan di pundak, atau genggaman tangan yang menenangkan."
        }
        love_language_tips = love_language_tips_map.get(love_language_primary, "")
        
        love_language_needs_map = {
            "Acts of Service": "Dukungan yang jelas, nyata, terarah, dan hubungan yang menghargai kompetensi/kemampuannya.",
            "Words of Affirmation": "Pengakuan tulus atas usaha yang dilakukan serta komunikasi jujur tanpa kata-kata yang berlebihan.",
            "Quality Time": "Kehadiran penuh secara emosional dan ruang komunikasi aktif untuk saling bertukar pikiran secara mendalam.",
            "Receiving Gifts": "Apresiasi atas perhatian kecil dan simbol kasih sayang yang diberikan secara tulus.",
            "Physical Touch": "Rasa aman, kehangatan emosional, dan peneguhan kehadiran secara fisik."
        }
        love_language_needs = love_language_needs_map.get(love_language_primary, "")
        
        # Recommendations sorting & classification
        intel_ranks = {name: rank for rank, (name, _) in enumerate(sorted_intel)}
        
        def get_ex_class(idx):
            if idx < 6:
                return "green"
            elif idx < 11:
                return "orange"
            return "red"
            
        def get_career_class(idx):
            if idx < 20:
                return "green"
            elif idx < 40:
                return "orange"
            return "red"
            
        # Build 2-column table for Extracurriculars
        sorted_ex = sorted(EXTRACURRICULARS, key=lambda x: intel_ranks.get(x["cat"], 10))
        extracurriculars_table = '<table class="rec-table" width="100%" style="table-layout: fixed;">\n'
        for i in range(8):
            ex1 = sorted_ex[i]
            ex2 = sorted_ex[i + 8]
            
            rank_class1 = get_ex_class(i)
            rank_class2 = get_ex_class(i + 8)
            
            extracurriculars_table += f"""  <tr>
    <td class="{rank_class1}" width="50%" style="padding: 8px 12px; font-size: 10.5pt;">{i+1}. {ex1["name"]}</td>
    <td class="{rank_class2}" width="50%" style="padding: 8px 12px; font-size: 10.5pt;">{i+9}. {ex2["name"]}</td>
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
                rank_class = get_career_class(idx)
                careers_table += f'    <td class="{rank_class}" width="20%" style="padding: 6px 8px; font-size: 9.5pt;">{idx+1}. {cr["name"]}</td>\n'
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
            fingerprint_b64=FINGERPRINT_B64,
            intelligence_rows=intel_rows_html,
            top_intelligence_1=top_int_1,
            top_intelligence_2=top_int_2,
            disc_primary=disc_primary,
            disc_secondary=disc_secondary,
            disc_primary_desc=disc_primary_desc,
            disc_secondary_desc=disc_secondary_desc,
            disc_strengths=disc_strengths,
            disc_develop=disc_develop,
            disc_team=disc_team,
            disc_presentation=disc_presentation,
            disc_pressure=disc_pressure,
            disc_decision=disc_decision,
            disc_tips=disc_tips,
            left_brain_pct=left_brain_pct,
            right_brain_pct=right_brain_pct,
            dominant_brain=dominant_brain,
            brain_dominance_desc=brain_desc,
            vak_visual=vak_visual_pct,
            vak_auditori=vak_auditori_pct,
            vak_kinestetik=vak_kinestetik_pct,
            vak_visual_rem=vak_visual_rem,
            vak_auditori_rem=vak_auditori_rem,
            vak_kinestetik_rem=vak_kinestetik_rem,
            dominant_vak=dominant_vak,
            vak_learning_advice=vak_advice,
            iq_pct=iq_pct,
            eq_pct=eq_pct,
            cq_pct=cq_pct,
            aq_pct=aq_pct,
            iq_pct_rem=iq_pct_rem,
            eq_pct_rem=eq_pct_rem,
            cq_pct_rem=cq_pct_rem,
            aq_pct_rem=aq_pct_rem,
            top_quotient=top_q,
            top_quotient_desc=top_q_desc,
            stimulation_tips_html=stimulation_tips_html,
            adaptability_kognitif=adaptability_kognitif,
            adaptability_afektif=adaptability_afektif,
            adaptability_reflektif=adaptability_reflektif,
            adaptability_kritis=adaptability_kritis,
            adaptability_kognitif_rem=adaptability_kognitif_rem,
            adaptability_afektif_rem=adaptability_afektif_rem,
            adaptability_reflektif_rem=adaptability_reflektif_rem,
            adaptability_kritis_rem=adaptability_kritis_rem,
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
