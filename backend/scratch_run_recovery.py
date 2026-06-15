import os
import re
import subprocess
import hashlib

def get_hash(b64_str):
    return hashlib.sha256(b64_str.strip().encode("utf-8")).hexdigest()

def main():
    repo_path = "e:\\my project\\ALLIA\\FPA"
    files_to_check = [
        "backend/app/report_engine/html_generator.py",
        "backend/cover.html",
        "backend/app/processing/cover.html"
    ]
    
    print("--- Searching Git History for Clean Vector Fingerprint Base64 ---")
    
    found_b64s = {}
    
    for relative_path in files_to_check:
        print(f"\nChecking file: {relative_path}")
        try:
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
                matches = re.findall(r'src="data:image/png;base64,([^"]+)"', file_res.stdout)
                for match in matches:
                    b64_str = match.strip()
                    if len(b64_str) > 5000:
                        h = get_hash(b64_str)
                        if h not in found_b64s:
                            commit_info = subprocess.run(
                                ["git", "show", "-s", "--format=%s (%ad)", commit_hash],
                                capture_output=True,
                                text=True,
                                encoding="utf-8",
                                errors="ignore",
                                cwd=repo_path
                            ).stdout.strip()
                            found_b64s[h] = {
                                "commit": commit_hash[:8],
                                "info": commit_info,
                                "len": len(b64_str),
                                "b64": b64_str
                            }
                            print(f"  [FOUND] Commit: {commit_hash[:8]} - {commit_info}")
                            print(f"          Length: {len(b64_str)}, SHA256: {h}")
        except Exception as e:
            print(f"  Error checking {relative_path}: {e}")

    # Compare with the brain candidates
    candidates = {
        "brain_candidate_b64_media__1781081434304_png.txt": "f17ef624d350458f58302e54a6aacc11b2e90e78ebe36be21d3ceca289a19ffa",
        "brain_candidate_b64_media__178236002239_png.txt": "90e898b683e82b457fab5eed47cb642616bf1e1a3ad3a2dea396238a9d1795b3" # correction: 1781236002239
    }
    
    # Correcting name for candidate 2
    candidates = {
        "brain_candidate_b64_media__1781081434304_png.txt": "f17ef624d350458f58302e54a6aacc11b2e90e78ebe36be21d3ceca289a19ffa",
        "brain_candidate_b64_media__1781236002239_png.txt": "90e898b683e82b457fab5eed47cb642616bf1e1a3ad3a2dea396238a9d1795b3"
    }

    print("\n--- Comparing Git History Hashes with Brain Candidates ---")
    for h, info in found_b64s.items():
        matched = False
        for cand, cand_hash in candidates.items():
            if h == cand_hash:
                print(f"Match found! Git SHA256 {h} (Commit {info['commit']}: {info['info']}) matches {cand}!")
                matched = True
        if not matched:
            print(f"No candidate match for Git SHA256 {h} (Commit {info['commit']}: {info['info']})")

if __name__ == "__main__":
    main()
