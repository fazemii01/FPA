import sys
import os
import shutil

def main():
    if len(sys.argv) < 2:
        print("Usage: python scratch_apply_specific.py <candidate_filename>")
        print("Example: python scratch_apply_specific.py brain_candidate_b64_media__1781236002239_png.txt")
        return
        
    candidate = sys.argv[1]
    if not os.path.exists(candidate):
        print(f"Error: Candidate file {candidate} not found.")
        return
        
    print(f"--- Applying Candidate: {candidate} ---")
    
    # 1. Copy to original_b64.txt
    shutil.copyfile(candidate, "original_b64.txt")
    print("Copied candidate to original_b64.txt.")
    
    # 2. Run scratch_apply_exact_user_html.py
    print("Running scratch_apply_exact_user_html.py...")
    try:
        import scratch_apply_exact_user_html
        # Reload module in case it was imported before
        import importlib
        importlib.reload(scratch_apply_exact_user_html)
        scratch_apply_exact_user_html.main()
        print("[SUCCESS] HTML template updated in html_generator.py.")
    except Exception as e:
        print(f"[ERROR] Failed to run update script: {e}")
        return
        
    # 3. Rebuild PDF
    print("Re-compiling report PDF...")
    try:
        from app.report_engine.html_generator import HTMLReportGenerator
        # Reload to get the fresh template
        import importlib
        import app.report_engine.html_generator
        importlib.reload(app.report_engine.html_generator)
        
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
        pdf_bytes = HTMLReportGenerator.generate_pdf_report("Raffasya Mock", mock_features)
        
        # Save output named after the candidate for easy comparison
        output_pdf = f"report_{candidate.replace('brain_candidate_b64_media__', '').replace('_png.txt', '')}.pdf"
        with open(output_pdf, "wb") as f:
            f.write(pdf_bytes)
        print(f"[SUCCESS] PDF generated successfully and saved to {output_pdf}!")
    except Exception as e:
        print(f"[ERROR] Failed to compile PDF: {e}")

if __name__ == "__main__":
    main()
