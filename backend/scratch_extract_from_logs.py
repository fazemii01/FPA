import os
import json
import re

def main():
    convo_id = "3c3b6b90-88fa-44d5-acd0-b5b0c093be10"
    log_path = f"C:\\Users\\fazemii01\\.gemini\\antigravity\\brain\\{convo_id}\\.system_generated\\logs\\transcript.jsonl"
    
    if not os.path.exists(log_path):
        print(f"Error: Log file not found at {log_path}")
        return
        
    print(f"Reading logs from {log_path}...")
    
    # Let's read the JSONL file and search for the user's message containing the base64 string
    target_pattern = r'src="data:image/png;base64,([^"]+)"'
    found_b64 = None
    
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                step = json.loads(line)
                # We want to check content in steps from USER
                source = step.get("source", "")
                content = step.get("content", "")
                
                # Check if this is the user's message containing the HTML cover code
                if "Tab Allia Finger - Cover" in content or "blue vector finger print is from this code" in content:
                    matches = re.findall(target_pattern, content)
                    for match in matches:
                        b64_candidate = match.strip()
                        # Exclude short or corrupted ones, we want the long vector fingerprint base64
                        if len(b64_candidate) > 10000:
                            found_b64 = b64_candidate
                            print(f"Successfully found valid base64 in log! (Length: {len(found_b64)})")
                            break
                if found_b64:
                    break
            except Exception as e:
                continue
                
    if found_b64:
        # Save it to original_b64.txt
        with open("original_b64.txt", "w", encoding="utf-8") as f:
            f.write(found_b64)
        print("Successfully saved recovered blue vector base64 to original_b64.txt!")
    else:
        print("Could not find the original base64 in the transcript logs.")

if __name__ == "__main__":
    main()
