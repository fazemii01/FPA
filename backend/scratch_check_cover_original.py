import os
import re
import hashlib

def get_hash(b64_str):
    return hashlib.sha256(b64_str.strip().encode("utf-8")).hexdigest()

def main():
    cover_path = "cover.html"
    if not os.path.exists(cover_path):
        cover_path = "app/processing/cover.html"
        
    if not os.path.exists(cover_path):
        print("cover.html not found.")
        return
        
    print(f"Reading {cover_path}...")
    with open(cover_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    matches = re.findall(r'src="data:image/(?:png|jpeg);base64,([^"]+)"', content)
    if not matches:
        print("No base64 images found in cover.html.")
        return
        
    cover_b64 = matches[0].strip()
    cover_hash = get_hash(cover_b64)
    print(f"cover.html base64 length: {len(cover_b64)}")
    print(f"cover.html base64 SHA256: {cover_hash}")
    
    candidates = [
        "brain_candidate_b64_media__1781081434304_png.txt",
        "brain_candidate_b64_media__1781236002239_png.txt"
    ]
    
    for cand in candidates:
        if os.path.exists(cand):
            with open(cand, "r", encoding="utf-8") as f:
                cand_b64 = f.read().strip()
            cand_hash = get_hash(cand_b64)
            print(f"{cand} SHA256: {cand_hash}")
            if cand_hash == cover_hash:
                print(f"==> MATCH FOUND: {cand} is the original cover.html fingerprint!")
            else:
                print(f"    No match for {cand}")

if __name__ == "__main__":
    main()
