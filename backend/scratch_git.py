import subprocess
import re

def main():
    try:
        # Get list of all commit hashes for the file
        result = subprocess.run(
            ["git", "log", "--format=%H", "backend/app/report_engine/html_generator.py"],
            capture_output=True,
            text=True,
            cwd="e:\\my project\\ALLIA\\FPA"
        )
        if not result.stdout:
            print("No commits found for backend/app/report_engine/html_generator.py")
            return
            
        hashes = result.stdout.strip().split("\n")
        print(f"Found {len(hashes)} commits in git log for this file.")
        
        for commit_hash in hashes:
            print(f"Checking commit {commit_hash}...")
            file_res = subprocess.run(
                ["git", "show", f"{commit_hash}:backend/app/report_engine/html_generator.py"],
                capture_output=True,
                text=True,
                cwd="e:\\my project\\ALLIA\\FPA"
            )
            if file_res.stdout:
                # Let's search for the fingerprint base64 string
                b64_match = re.search(r'src="data:image/png;base64,([^"]+)"', file_res.stdout)
                if b64_match:
                    b64_str = b64_match.group(1)
                    if "Requires a path while reporting success" not in b64_str:
                        print(f"Success! Found uncorrupted base64 in commit {commit_hash} (length: {len(b64_str)}).")
                        with open("original_b64.txt", "w") as f:
                            f.write(b64_str)
                        print("Saved original base64 string to original_b64.txt")
                        return
                    else:
                        print("  (This commit contains the corrupted version)")
                else:
                    print("  (Could not find base64 string in this commit)")
            else:
                print(f"  (Failed to read file from commit {commit_hash})")
                
        print("Completed search, no uncorrupted base64 string found in any commit history.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
