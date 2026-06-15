import os
import re
import subprocess

def main():
    repo_path = "e:\\my project\\ALLIA\\FPA"
    backend_path = os.path.join(repo_path, "backend")
    
    # Files relative to the backend directory (where we run the script)
    files_rel_backend = [
        "app/report_engine/html_generator.py",
        "cover.html",
        "app/processing/cover.html"
    ]
    
    print("--- Restoring Ring/Fingerprint and Removing Nodes ---")
    
    # 1. Discard previous changes to get a clean slate
    print("Discarding previous changes via git checkout...")
    for f in files_rel_backend:
        git_path = f"backend/{f}"
        try:
            subprocess.run(
                ["git", "checkout", "--", git_path],
                cwd=repo_path,
                capture_output=True
            )
            print(f"  Restored {git_path} to original state.")
        except Exception as e:
            print(f"  Error restoring {git_path}: {e}")
            
    # 2. Remove ONLY the node elements
    node_patterns = [
        r'\s*<div class="node tl"></div>',
        r'\s*<div class="node tr"></div>',
        r'\s*<div class="node bl"></div>',
        r'\s*<div class="node br"></div>'
    ]
    
    any_updated = False
    for f in files_rel_backend:
        full_path = os.path.join(backend_path, f)
            
        if not os.path.exists(full_path):
            print(f"File not found: {full_path}")
            continue
            
        print(f"Removing nodes from {full_path}...")
        with open(full_path, "r", encoding="utf-8") as file_obj:
            content = file_obj.read()
            
        updated = False
        for pattern in node_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, "", content)
                updated = True
                
        if updated:
            with open(full_path, "w", encoding="utf-8") as file_obj:
                file_obj.write(content)
            print(f"  Successfully removed nodes.")
            any_updated = True
        else:
            print(f"  No node elements found.")
            
    if any_updated:
        # Re-compile report PDF
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
            pdf_bytes = HTMLReportGenerator.generate_pdf_report("Raffasya Mock No Nodes", mock_features)
            with open("real_feature_report.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("[SUCCESS] real_feature_report.pdf generated successfully with ring/fingerprint but without the nodes!")
        except Exception as e:
            print(f"[ERROR] Failed to compile PDF: {e}")

if __name__ == "__main__":
    main()
