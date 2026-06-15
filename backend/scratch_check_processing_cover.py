import os
import re

def main():
    cover_path = "e:\\my project\\ALLIA\\FPA\\backend\\app\\processing\\cover.html"
    if not os.path.exists(cover_path):
        print(f"Error: {cover_path} not found.")
        return
        
    print(f"Found cover.html at {cover_path} (Size: {os.path.getsize(cover_path)} bytes).")
    
    with open(cover_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Search for base64 image pattern
    matches = re.findall(r'src="data:image/(?:png|jpeg);base64,([^"]+)"', content)
    print(f"Found {len(matches)} base64 images in the file.")
    
    for i, match in enumerate(matches):
        b64_str = match.strip()
        print(f"Image {i}:")
        print(f"  Length: {len(b64_str)}")
        print(f"  Snippet: {b64_str[:60]}...{b64_str[-60:]}")
        
        # Save to candidate file
        filename = f"cover_candidate_b64_{i}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(b64_str)
        print(f"  Saved base64 content to {filename}")

if __name__ == "__main__":
    main()
