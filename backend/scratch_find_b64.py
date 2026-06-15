import os
import base64
import re
import subprocess

def search_files():
    # 1. Let's fix the git checker first to use utf-8 with errors ignored
    print("Checking git history with utf-8 encoding...")
    try:
        result = subprocess.run(
            ["git", "log", "--format=%H", "backend/app/report_engine/html_generator.py"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            cwd="e:\\my project\\ALLIA\\FPA"
        )
        if result.stdout:
            hashes = result.stdout.strip().split("\n")
            print(f"Found {len(hashes)} commits.")
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
                    b64_match = re.search(r'src="data:image/png;base64,([^"]+)"', file_res.stdout)
                    if b64_match:
                        b64_str = b64_match.group(1).strip()
                        if "Requires a path while reporting success" not in b64_str:
                            print(f"Success! Found uncorrupted base64 in commit {h} (len: {len(b64_str)}).")
                            with open("original_b64.txt", "w") as f:
                                f.write(b64_str)
                            return True
        else:
            print("No commits found.")
    except Exception as e:
        print(f"Git error: {e}")

    # 2. Check if we have any png/jpeg in 'result image' that we can convert to base64
    print("\nChecking local result images...")
    img_dir = "e:\\my project\\ALLIA\\FPA\\backend\\result image"
    if os.path.exists(img_dir):
        files = os.listdir(img_dir)
        print(f"Files in result image: {files}")
        for file in files:
            if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg"):
                full_path = os.path.join(img_dir, file)
                size = os.path.getsize(full_path)
                print(f"  {file} ({size} bytes)")
    else:
        print(f"Directory {img_dir} does not exist.")
        
    return False

if __name__ == "__main__":
    search_files()
