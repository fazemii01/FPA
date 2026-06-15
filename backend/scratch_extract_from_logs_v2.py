import os
import json
import re
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
    convo_id = "3c3b6b90-88fa-44d5-acd0-b5b0c093be10"
    log_dir = f"C:\\Users\\fazemii01\\.gemini\\antigravity\\brain\\{convo_id}\\.system_generated\\logs"
    
    # We want to exclude the corrupted grayscale one.
    # The corrupted grayscale base64 starts with "iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAAAAADRE4smAAAgAElMR"
    corrupted_prefix = "iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAAAAADRE4smAAAgAElMR"
    
    files = ["transcript_full.jsonl", "transcript.jsonl"]
    candidates = {}
    
    print("--- Extracting Base64 Images from Conversation Logs ---")
    
    for filename in files:
        filepath = os.path.join(log_dir, filename)
        if not os.path.exists(filepath):
            print(f"File {filename} not found.")
            continue
            
        print(f"\nProcessing {filename}...")
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_idx, line in enumerate(f):
                # Search for base64 patterns: src="data:image/png;base64,..." or similar
                matches = re.findall(r'data:image/(?:png|jpeg);base64,([A-Za-z0-9+/=\s\n\r]+)', line)
                for match in matches:
                    # Clean up the string (remove spaces, quotes, etc. that might be captured by regex)
                    # We only want characters belonging to base64 charset
                    b64_str = re.sub(r'[^A-Za-z0-9+/=]', '', match)
                    
                    if len(b64_str) < 5000:
                        continue # Skip short strings (icons/logos/etc.)
                        
                    # Skip the known corrupted grayscale scan
                    if b64_str.startswith(corrupted_prefix):
                        continue
                        
                    img_type = check_base64_image(b64_str)
                    if img_type in ["PNG", "JPEG"]:
                        # Store by its unique prefix
                        prefix = b64_str[:40]
                        if prefix not in candidates:
                            candidates[prefix] = {
                                "b64": b64_str,
                                "type": img_type,
                                "length": len(b64_str),
                                "source_file": filename,
                                "line": line_idx + 1
                            }
                            print(f"Found candidate: Length {len(b64_str)}, Type {img_type} (from {filename} line {line_idx+1})")
                            print(f"  Prefix: {b64_str[:60]}...")
                            
    if not candidates:
        print("\nNo unique valid base64 images found in the logs that differ from the corrupted grayscale one.")
        return
        
    print(f"\nTotal unique candidates found: {len(candidates)}")
    for idx, (prefix, info) in enumerate(candidates.items()):
        cand_b64_file = f"log_candidate_b64_{idx}.txt"
        cand_img_file = f"log_candidate_img_{idx}.{'png' if info['type'] == 'PNG' else 'jpg'}"
        
        with open(cand_b64_file, "w", encoding="utf-8") as f:
            f.write(info["b64"])
            
        try:
            img_data = base64.b64decode(info["b64"])
            with open(cand_img_file, "wb") as f:
                f.write(img_data)
            print(f"Saved candidate {idx} (length: {info['length']}) to {cand_b64_file} and {cand_img_file}")
        except Exception as e:
            print(f"Failed to save candidate {idx}: {e}")

if __name__ == "__main__":
    main()
