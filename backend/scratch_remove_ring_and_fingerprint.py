import os
import re

def remove_elements_from_file(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return False
        
    print(f"Processing {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    updated = False
    
    # 1. Remove the ring div: <div class="ring"></div>
    ring_pattern = r'<div class="ring"></div>'
    if re.search(ring_pattern, content):
        content = re.sub(ring_pattern, "<!-- removed ring -->", content)
        print("  Removed <div class='ring'></div>")
        updated = True
        
    # 2. Remove the ring-inner div and its contents: <div class="ring-inner">...</div>
    ring_inner_pattern = r'<div class="ring-inner">.*?</div>'
    if re.search(ring_inner_pattern, content, re.DOTALL):
        content = re.sub(ring_inner_pattern, "<!-- removed ring-inner -->", content, flags=re.DOTALL)
        print("  Removed <div class='ring-inner'>...</div>")
        updated = True
        
    # If the previous step left any raw fingerprint img tags, remove them too
    img_pattern = r'<img class="fingerprint".*?>'
    if re.search(img_pattern, content, re.DOTALL):
        content = re.sub(img_pattern, "<!-- removed fingerprint image -->", content, flags=re.DOTALL)
        print("  Removed stray fingerprint image tag.")
        updated = True
        
    if updated:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("  Successfully saved changes.")
        return True
    else:
        print("  No changes needed.")
        return False

def main():
    files = [
        "app/report_engine/html_generator.py",
        "cover.html",
        "app/processing/cover.html"
    ]
    
    any_updated = False
    for f in files:
        if remove_elements_from_file(f):
            any_updated = True
            
    if any_updated:
        print("\nRe-compiling report PDF...")
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
            pdf_bytes = HTMLReportGenerator.generate_pdf_report("Raffasya Mock No Ring", mock_features)
            with open("real_feature_report.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("[SUCCESS] real_feature_report.pdf regenerated successfully!")
        except Exception as e:
            print(f"[ERROR] Failed to compile PDF: {e}")

if __name__ == "__main__":
    main()
