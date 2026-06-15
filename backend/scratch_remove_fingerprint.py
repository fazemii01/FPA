import os
import re

def remove_from_file(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return False
        
    print(f"Processing {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Regex to match <div class="ring-inner">...</div> non-greedily
    pattern = r'<div class="ring-inner">.*?</div>'
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        print(f"  Found ring-inner block (Length: {len(match.group(0))} characters).")
        # Replace with empty string
        new_content = re.sub(pattern, "<!-- removed ring-inner -->", content, flags=re.DOTALL)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("  Successfully removed ring-inner block.")
        return True
    else:
        print("  ring-inner block not found.")
        # Fallback search for just the image tag if ring-inner is formatted differently
        img_pattern = r'<img class="fingerprint".*?>'
        img_match = re.search(img_pattern, content, re.DOTALL)
        if img_match:
            print(f"  Found fingerprint image tag (Length: {len(img_match.group(0))} characters).")
            new_content = re.sub(img_pattern, "<!-- removed fingerprint image -->", content, flags=re.DOTALL)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("  Successfully removed fingerprint image tag.")
            return True
        else:
            print("  fingerprint image tag not found.")
            return False

def main():
    files = [
        "app/report_engine/html_generator.py",
        "cover.html",
        "app/processing/cover.html"
    ]
    
    any_updated = False
    for f in files:
        if remove_from_file(f):
            any_updated = True
            
    if any_updated:
        print("\nRe-compiling report PDF to verify layout...")
        try:
            from app.report_engine.html_generator import HTMLReportGenerator
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
            pdf_bytes = HTMLReportGenerator.generate_pdf_report("Raffasya Mock No Fingerprint", mock_features)
            with open("real_feature_report.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("[SUCCESS] real_feature_report.pdf generated successfully without fingerprint image!")
        except Exception as e:
            print(f"[ERROR] Failed to compile PDF: {e}")

if __name__ == "__main__":
    main()
