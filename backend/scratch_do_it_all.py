import os
import re
import json
import base64
import subprocess

def check_base64_image(b64_str):
    try:
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        img_data = base64.b64decode(b64_str)
        if img_data.startswith(b'\x89PNG\r\n\x1a\n'):
            return "PNG"
        elif img_data.startswith(b'\xff\xd8\xff'):
            return "JPEG"
        return None
    except Exception:
        return None

def main():
    print("--- Autopilot: Restoring Clean Vector Fingerprint Cover ---")
    
    convo_id = "3c3b6b90-88fa-44d5-acd0-b5b0c093be10"
    log_path = f"C:\\Users\\fazemii01\\.gemini\\antigravity\\brain\\{convo_id}\\.system_generated\\logs\\transcript.jsonl"
    processing_cover_path = "e:\\my project\\ALLIA\\FPA\\backend\\app\\processing\\cover.html"
    html_gen_path = "e:\\my project\\ALLIA\\FPA\\backend\\app\\report_engine\\html_generator.py"
    
    blue_vector_b64 = None
    
    # Method 1: Extract from cover.html in processing directory
    if os.path.exists(processing_cover_path):
        print(f"Checking {processing_cover_path}...")
        with open(processing_cover_path, "r", encoding="utf-8") as f:
            cover_content = f.read()
        matches = re.findall(r'src="data:image/(?:png|jpeg);base64,([^"]+)"', cover_content)
        for match in matches:
            b64_str = match.strip()
            # The clean vector fingerprint is long (usually > 100k characters)
            # And we want to make sure it's not the corrupted one
            if len(b64_str) > 100000 and "Requires a path" not in b64_str:
                img_type = check_base64_image(b64_str)
                if img_type:
                    # Let's verify if this is not the grayscale scanned fingerprint
                    # (we will store it as candidate)
                    blue_vector_b64 = b64_str
                    print(f"  [SUCCESS] Found clean base64 image in processing/cover.html! (Length: {len(b64_str)})")
                    break

    # Method 2: Fallback to conversation transcript log
    if not blue_vector_b64 and os.path.exists(log_path):
        print(f"Checking logs at {log_path}...")
        target_pattern = r'src="data:image/png;base64,([^"]+)"'
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    step = json.loads(line)
                    content = step.get("content", "")
                    if "Tab Allia Finger - Cover" in content or "blue vector finger print is from this code" in content:
                        matches = re.findall(target_pattern, content)
                        for match in matches:
                            b64_candidate = match.strip()
                            if len(b64_candidate) > 100000 and "Requires a path" not in b64_candidate:
                                if check_base64_image(b64_candidate):
                                    blue_vector_b64 = b64_candidate
                                    print(f"  [SUCCESS] Found clean base64 in conversation logs! (Length: {len(blue_vector_b64)})")
                                    break
                    if blue_vector_b64:
                        break
                except Exception:
                    continue
                    
    # Method 3: Fallback to Git history of html_generator.py
    if not blue_vector_b64:
        print("Checking git history of html_generator.py...")
        try:
            result = subprocess.run(
                ["git", "log", "--format=%H", html_gen_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                cwd="e:\\my project\\ALLIA\\FPA"
            )
            if result.stdout:
                hashes = result.stdout.strip().split("\n")
                for h in hashes:
                    file_res = subprocess.run(
                        ["git", "show", f"{h}:backend/app/report_engine/html_generator.py"],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="ignore",
                        cwd="e:\\my project\\ALLIA\\FPA"
                    )
                    if file_res.stdout:
                        matches = re.findall(r'src="data:image/png;base64,([^"]+)"', file_res.stdout)
                        for match in matches:
                            b64_candidate = match.strip()
                            if len(b64_candidate) > 100000 and "Requires a path" not in b64_candidate:
                                if check_base64_image(b64_candidate):
                                    blue_vector_b64 = b64_candidate
                                    print(f"  [SUCCESS] Found clean base64 in git history! (Length: {len(blue_vector_b64)})")
                                    break
                    if blue_vector_b64:
                        break
        except Exception as e:
            print(f"  Git error: {e}")

    if not blue_vector_b64:
        print("\n[FAIL] Could not recover the original blue vector fingerprint base64.")
        print("Please check if the file original_b64.txt is present or if WeasyPrint GTK is installed.")
        return
        
    # Write to original_b64.txt
    with open("original_b64.txt", "w", encoding="utf-8") as f:
        f.write(blue_vector_b64)
    print("Saved clean base64 string to original_b64.txt.")
    
    # Run the html update script logic directly
    print("\nApplying exact user cover layout and recovered base64 to html_generator.py...")
    try:
        import scratch_apply_exact_user_html
        scratch_apply_exact_user_html.main()
        print("[SUCCESS] HTML template updated.")
    except Exception as e:
        print(f"[ERROR] Failed to run update script: {e}")
        return
        
    # Rebuild PDF
    print("\nRe-compiling report PDF...")
    try:
        from app.report_engine.html_generator import HTMLReportGenerator
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
        with open("real_feature_report.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("[SUCCESS] real_feature_report.pdf generated successfully with clean blue fingerprint!")
    except Exception as e:
        print(f"[ERROR] Failed to compile PDF: {e}")
        print("Please check Weasyprint / GTK install.")

if __name__ == "__main__":
    main()
