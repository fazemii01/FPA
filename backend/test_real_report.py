import os
import sys
from app.report_engine.html_generator import HTMLReportGenerator

def test_real_report_generation():
    print("Testing real HTMLReportGenerator.calculate_dmit_metrics with mock finger features...")
    
    mock_features = [
        {"finger_position": "left_thumb", "pattern_type": "whorl", "ridge_count": 18},
        {"finger_position": "left_index", "pattern_type": "loop", "ridge_count": 15},
        {"finger_position": "left_middle", "pattern_type": "loop", "ridge_count": 16},
        {"finger_position": "left_ring", "pattern_type": "whorl", "ridge_count": 17},
        {"finger_position": "left_pinky", "pattern_type": "loop", "ridge_count": 14},
        {"finger_position": "right_thumb", "pattern_type": "whorl", "ridge_count": 19},
        {"finger_position": "right_index", "pattern_type": "loop", "ridge_count": 13},
        {"finger_position": "right_middle", "pattern_type": "loop", "ridge_count": 15},
        {"finger_position": "right_ring", "pattern_type": "whorl", "ridge_count": 18},
        {"finger_position": "right_pinky", "pattern_type": "loop", "ridge_count": 12},
    ]

    print("Calculating DMIT metrics...")
    metrics = HTMLReportGenerator.calculate_dmit_metrics(mock_features)
    print("Calculated Metrics:")
    for key, val in metrics.items():
        print(f"  {key}: {val}")
        
    print("\nGenerating HTML report...")
    html_content = HTMLReportGenerator.generate_html_report("Raffasya Mock", mock_features)
    assert html_content and len(html_content) > 1000, "HTML template generated is empty!"
    print(f"HTML Template compiled successfully (length: {len(html_content)} characters).")

    print("\nCompiling to PDF (real_feature_report.pdf)...")
    output_pdf = "real_feature_report.pdf"
    if os.path.exists(output_pdf):
        os.remove(output_pdf)
        
    try:
        pdf_bytes = HTMLReportGenerator.generate_pdf_report("Raffasya Mock", mock_features)
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
    test_real_report_generation()
