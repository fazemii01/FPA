import os
import re
import subprocess
import base64

def check_base64_image(b64_str):
    try:
        # Remove any whitespace or header
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        img_data = base64.b64decode(b64_str)
        # Check if it starts with PNG header
        if img_data.startswith(b'\x89PNG\r\n\x1a\n'):
            return "PNG"
        elif img_data.startswith(b'\xff\xd8\xff'):
            return "JPEG"
        return "Unknown Format"
    except Exception:
        return "Invalid Base64"

def main():
    repo_path = "e:\\my project\\ALLIA\\FPA"
    files_to_check = [
        "backend/app/report_engine/html_generator.py",
        "backend/cover.html",
        "backend/app/processing/cover.html" # Let's also check other possible locations
    ]
    
    print("--- Searching Git History for Clean Vector Fingerprint Base64 ---")
    
    found_b64s = []
    
    for relative_path in files_to_check:
        print(f"\nChecking file: {relative_path}")
        try:
            # Get commit hashes affecting this file
            result = subprocess.run(
                ["git", "log", "--format=%H", relative_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                cwd=repo_path
            )
            if not result.stdout:
                print(f"  No git history found for {relative_path}")
                continue
                
            hashes = result.stdout.strip().split("\n")
            print(f"  Found {len(hashes)} commits affecting this file.")
            
            for commit_hash in hashes:
                file_res = subprocess.run(
                    ["git", "show", f"{commit_hash}:{relative_path}"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    cwd=repo_path
                )
                if not file_res.stdout:
                    continue
                
                # Search for base64 fingerprint image pattern
                matches = re.findall(r'src="data:image/(?:png|jpeg);base64,([^"]+)"', file_res.stdout)
                for match in matches:
                    b64_str = match.strip()
                    img_type = check_base64_image(b64_str)
                    
                    if img_type in ["PNG", "JPEG"]:
                        # Exclude the corrupted one and the one matching current 0_default
                        # Let's save unique valid base64 strings
                        if b64_str not in [x[1] for x in found_b64s]:
                            # Get commit info
                            commit_info = subprocess.run(
                                ["git", "show", "-s", "--format=%s (%ad)", commit_hash],
                                capture_output=True,
                                text=True,
                                encoding="utf-8",
                                errors="ignore",
                                cwd=repo_path
                            ).stdout.strip()
                            found_b64s.append((commit_hash, b64_str, img_type, commit_info))
                            print(f"  [FOUND] Commit: {commit_hash[:8]} - {commit_info}")
                            print(f"          Format: {img_type}, Length: {len(b64_str)}")
                            print(f"          Snippet: {b64_str[:60]}...{b64_str[-60:]}")
        except Exception as e:
            print(f"  Error checking {relative_path}: {e}")

    if found_b64s:
        print(f"\nTotal unique valid images found: {len(found_b64s)}")
        # Save them as separate txt files so the user/agent can inspect or apply them
        for idx, (commit_hash, b64_str, img_type, commit_info) in enumerate(found_b64s):
            filename = f"recovered_b64_{idx}_{commit_hash[:8]}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(b64_str)
            print(f"Saved candidate {idx} to '{filename}' (Commit: {commit_info})")
            
            # Let's also decode and save the image file for the user to visually inspect
            try:
                img_data = base64.b64decode(b64_str)
                img_ext = "png" if img_type == "PNG" else "jpg"
                img_filename = f"recovered_img_{idx}_{commit_hash[:8]}.{img_ext}"
                with open(img_filename, "wb") as f:
                    f.write(img_data)
                print(f"  -> Decoded image saved to '{img_filename}'")
            except Exception as e:
                print(f"  -> Failed to decode and save image: {e}")
    else:
        print("\nNo unique valid base64 images found in git history.")

if __name__ == "__main__":
    main()
