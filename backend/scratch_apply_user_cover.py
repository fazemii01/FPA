import re
import os

def main():
    file_path = "e:\\my project\\ALLIA\\FPA\\backend\\app\\report_engine\\html_generator.py"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # User's unscaled styles for the cover page
    # Note: we change .page to .page-cover to isolate it from the other pages
    # Also we use double curly braces {{ }} for the python template string
    user_styles = """
        .page-cover {{
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
            padding-top: 70px;
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
        .title-wrap {{ margin-top: 26px; }}
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
            margin-top: 26px;
        }}
        .badge {{
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
            width: 600px; height: 510px;
            margin: 40px auto 0;
        }}
        /* dashed orbit */
        .orbit {{
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%,-50%);
            width: 460px; height: 460px;
            border: 2px dashed #c7ccdd;
            border-radius: 50%;
        }}
        /* segmented ring */
        .ring {{
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%,-50%);
            width: 320px; height: 320px;
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
            width: 250px; height: 250px;
            background: #fff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 6px 20px rgba(0,0,0,.08);
        }}
        .fingerprint {{ width: 175px; height: 175px; object-fit: contain; }}

        /* connector nodes on the ring */
        .node {{
            position: absolute;
            width: 30px; height: 30px;
            background: #fff;
            border: 4px solid #1a2456;
            border-radius: 50%;
            z-index: 4;
        }}
        .node.tl {{ top: 92px;  left: 218px; border-color: #2a3a8c; }}
        .node.tr {{ top: 92px;  right: 218px; border-color: #f06a1e; }}
        .node.bl {{ bottom: 92px; left: 218px; border-color: #2a3a8c; }}
        .node.br {{ bottom: 92px; right: 218px; border-color: #0f9c8e; }}

        /* corner feature circles */
        .feat {{
            position: absolute;
            width: 130px; height: 130px;
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
            inset:10px;
            border-radius:50%;
            border:3px solid currentColor;
            opacity:.18;
        }}
        .feat.brain {{ top: 30px; left: 6px; color: #1a2456; }}
        .feat.brain {{ border: 6px solid #1a2456; }}
        .feat.growth {{ top: 30px; right: 6px; color: #f06a1e; border:6px solid #f06a1e;}}
        .feat.book {{ bottom: 6px; left: 56px; color: #2a3a8c; border:6px solid #2a3a8c;}}
        .feat.compass {{ bottom: 6px; right: 56px; color: #0f9c8e; border:6px solid #0f9c8e;}}
        .feat svg {{ width: 64px; height: 64px; }}

        /* Name field */
        .name-block {{
            position: absolute;
            bottom: 90px;
            left: 110px;
            right: 110px;
            z-index: 6;
        }}
        .name-label {{
            position: absolute;
            top: -26px; left: 30px;
            background: #1a2456;
            color: #fff;
            font-weight: 700;
            font-size: 23px;
            letter-spacing: 1px;
            padding: 12px 38px 12px 64px;
            border-radius: 30px;
            z-index: 2;
            display:flex; align-items:center;
        }}
        .name-label .avatar {{
            position:absolute;
            left: -2px; top: 50%;
            transform: translateY(-50%);
            width: 50px; height: 50px;
            background: #1a2456;
            border: 3px solid #fff;
            border-radius: 50%;
            display:flex; align-items:center; justify-content:center;
        }}
        .name-box {{
            border: 2px solid #e3e6ef;
            border-radius: 22px;
            height: 200px;
            background:#fff;
            display:flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            padding: 0 50px 46px;
        }}
        .name-line {{
            width: 100%;
            border-bottom: 3px dotted #9aa1b8;
            height: 2px;
        }}
    """
    
    # Read the clean base64 string
    with open("original_b64.txt", "r", encoding="utf-8") as f:
        clean_b64 = f.read().strip()
        
    # User's HTML cover page
    user_html = f"""
    <!-- Page 1: COVER -->
    <div class="page-cover">
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
            <div class="badge">ADVANCE REPORT</div>
            <div class="badge-line right"></div>
          </div>

          <!-- Infographic -->
          <div class="info">
            <div class="orbit"></div>
            <div class="ring"></div>
            <div class="ring-inner">
              <img class="fingerprint" src="data:image/png;base64,{clean_b64}" alt="fingerprint">
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
            <div style="width: 100%; text-align: center; font-size: 24px; font-weight: 700; color: #1a2456; margin-bottom: 8px;">{{participant_name}}</div>
            <div class="name-line"></div>
          </div>
        </div>
    </div>
    """
    
    # We replace the styles in html_generator.py
    # Pattern to match starting from .page-cover {{ to .name-line {{ ... }}
    style_pattern = r'\.page-cover\s*\{\{.*?\n\s*\.name-line\s*\{\{\s*width:\s*100%;\s*border-bottom:\s*2px\s*dotted\s*#9aa1b8;\s*height:\s*2px;\s*\}\}'
    
    # Let's search using regex with DOTALL to match newlines
    match = re.search(style_pattern, content, re.DOTALL)
    if match:
        print("Style block match found in html_generator.py!")
        # Replace the style block
        new_content = re.sub(style_pattern, user_styles.strip(), content, flags=re.DOTALL)
    else:
        print("Style block match not found! Let's search with a broader pattern.")
        # fallback search
        fallback_pattern = r'\.page-cover\s*\{\{.*?\n\s*\}\s*\n\s*/\* Headers and Typography \*/'
        match_fb = re.search(fallback_pattern, new_content if 'new_content' in locals() else content, re.DOTALL)
        if match_fb:
            print("Fallback style match found!")
            new_content = re.sub(fallback_pattern, user_styles.strip() + "\n\n        /* Headers and Typography */", content, flags=re.DOTALL)
        else:
            print("Could not match style block.")
            return

    # Now replace the HTML block
    html_pattern = r'<!-- Page 1: COVER -->.*?<!-- Page 2: MULTIPLE INTELLIGENCE -->'
    match_html = re.search(html_pattern, new_content, re.DOTALL)
    if match_html:
        print("HTML block match found in html_generator.py!")
        final_content = re.sub(html_pattern, user_html.strip() + "\n\n    <!-- Page 2: MULTIPLE INTELLIGENCE -->", new_content, flags=re.DOTALL)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        print("Successfully applied user's unscaled cover styles and HTML template!")
    else:
        print("HTML cover block not found!")

if __name__ == "__main__":
    main()
