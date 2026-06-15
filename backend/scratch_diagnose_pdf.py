import sys
import os

# Bind GTK runtime directories dynamically on Windows
if sys.platform == 'win32':
    for path in [
        r'C:\Program Files\GTK3-Runtime\bin',
        r'C:\Program Files (x86)\GTK3-Runtime\bin',
        r'C:\msys64\mingw64\bin'
    ]:
        if os.path.exists(path):
            if path not in os.environ['PATH']:
                os.environ['PATH'] = path + os.pathsep + os.environ['PATH']
            if hasattr(os, 'add_dll_directory'):
                try:
                    os.add_dll_directory(path)
                except Exception:
                    pass
            break

print("--- PDF Engine Diagnostics ---")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Check xhtml2pdf
try:
    import xhtml2pdf
    from xhtml2pdf import pisa
    print("[OK] xhtml2pdf is installed and can be imported.")
except ImportError as e:
    print(f"[FAIL] xhtml2pdf is NOT installed or cannot be imported: {e}")

# Check WeasyPrint
try:
    import weasyprint
    print("[OK] weasyprint package is installed.")
    # Try creating a dummy HTML object to ensure DLLs are loaded
    wp_html = weasyprint.HTML(string="<h1>Test</h1>")
    print("[OK] WeasyPrint initialized successfully.")
except ImportError as e:
    print(f"[FAIL] weasyprint package is NOT installed in python environment: {e}")
except OSError as e:
    print(f"[FAIL] WeasyPrint package is installed but failed to load system libraries (e.g. GTK):")
    print(f"       {e}")
    print("\n   >>> NOTE: WeasyPrint requires the GTK+ runtime on Windows.")
    print("   >>> Please install GTK+ (e.g., from https://github.com/tschoonj/GTK-for-Windows-runtime-environment-installer/releases)")
    print("   >>> and ensure its 'bin' directory is added to your system PATH.")
except Exception as e:
    print(f"[FAIL] Unexpected error importing WeasyPrint: {e}")

# Check what engine html_generator.py will use
try:
    from app.report_engine.html_generator import weasyprint as hg_wp, pisa as hg_pisa
    print("\nReport Generator Status:")
    print(f"  HTMLReportGenerator.weasyprint: {'Available' if hg_wp is not None else 'None (Fallback active)'}")
    print(f"  HTMLReportGenerator.pisa: {'Available' if hg_pisa is not None else 'None'}")
    
    if hg_wp is None:
        print("\nWARNING: WeasyPrint is NOT active. The PDF will compile via xhtml2pdf,")
        print("which ignores CSS3 flexbox, transitions, transform (rotation/skew), border-radius,")
        print("and gradients. This makes the cover page render as plain text (Image 1).")
    else:
        print("\nSUCCESS: WeasyPrint is active. The PDF cover page should render as Image 2.")
except Exception as e:
    print(f"\n[ERROR] Failed to import HTMLReportGenerator: {e}")
