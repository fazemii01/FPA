import os
import sys
from app.report_engine.html_generator import HTMLReportGenerator

def test_report_compilation():
    print("Monkeypatching HTMLReportGenerator.calculate_dmit_metrics to return exact results from manual_Raffasya.pdf...")
    
    # Exact extracted metrics for Raffasya from manual_Raffasya.pdf
    exact_metrics = {
        "intelligences": {
            "intrapersonal": 19.19,
            "logical": 8.58,
            "linguistik": 14.06,
            "naturalis": 10.20,
            "interpersonal": 10.66,
            "visual-spasial": 9.69,
            "musikal": 16.57,
            "kinestetik": 11.05
        },
        "quotients": {
            "IQ": 22.64,
            "EQ": 29.85,
            "CQ": 26.26,
            "AQ": 21.25
        },
        "brain": {
            "left": 52.24,
            "right": 47.76
        },
        "vak": {
            "visual": 26.97,
            "auditori": 42.43,
            "kinestetik": 30.60
        },
        "adaptability": {
            "kognitif": 50.0,
            "afektif": 50.0,
            "reflektif": 0.0,
            "kritis": 0.0
        }
    }
    
    # Override the calculation method to feed exact metrics to the generator
    HTMLReportGenerator.calculate_dmit_metrics = lambda features: exact_metrics

    print("Testing generate_html_report generation using Raffasya's real data...")
    html_content = HTMLReportGenerator.generate_html_report("Raffasya", [])
    assert html_content and len(html_content) > 1000, "HTML template generated is empty!"
    print(f"HTML Template compiled successfully (length: {len(html_content)} characters).")

    print("\nAttempting to compile to PDF...")
    output_pdf = "mock_report.pdf"
    if os.path.exists(output_pdf):
        os.remove(output_pdf)
        
    try:
        pdf_bytes = HTMLReportGenerator.generate_pdf_report("Raffasya", [])
        with open(output_pdf, "wb") as f:
            f.write(pdf_bytes)
        print(f"[SUCCESS] PDF compiled successfully and written to {os.path.abspath(output_pdf)}")
        
        # Parse PDF using pypdf to verify layout
        print("\nVerifying PDF structure using pypdf...")
        import pypdf
        reader = pypdf.PdfReader(output_pdf)
        page_count = len(reader.pages)
        print(f"  Page Count: {page_count}")
        assert page_count == 10, f"Error: Page count is {page_count}, expected exactly 10!"
        print("  [SUCCESS] Page count is exactly 10!")
        
        # Extract and verify text
        full_text = ""
        for i, page in enumerate(reader.pages):
            full_text += page.extract_text() or ""
            
        print("  Checking for text smushing / fused words...")
        fused_words = ["SosiologiAntropologi", "Seni MusikEntrepreneurship", "BandKerohanian", "Internasionalllmu"]
        for word in fused_words:
            assert word not in full_text, f"Error: Found fused word '{word}' in PDF text!"
        print("  [SUCCESS] No fused words found! Columns separated correctly.")
        
        print("  Checking for header inversions (ISCD vs DISC)...")
        assert "ISCD" not in full_text, "Error: Found header inversion 'ISCD' in PDF text!"
        assert "DISC" in full_text, "Error: Header 'DISC' is missing from PDF text!"
        print("  [SUCCESS] DISC header extracted correctly without layout inversion!")
        
        print("\nAll layout and text extraction checks passed successfully!")
        
    except RuntimeError as e:
        print("\n[DEPENDENCY WARNING] PDF could not be compiled due to missing PDF libraries:")
        print(f"  {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during PDF compilation/verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_report_compilation()
