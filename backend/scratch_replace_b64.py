import re
import os

def main():
    # Read the clean base64 string
    b64_path = "e:\\my project\\ALLIA\\FPA\\backend\\original_b64.txt"
    if not os.path.exists(b64_path):
        print(f"Error: {b64_path} not found.")
        return
        
    with open(b64_path, "r", encoding="utf-8") as f:
        clean_b64 = f.read().strip()
        
    # Read html_generator.py
    file_path = "e:\\my project\\ALLIA\\FPA\\backend\\app\\report_engine\\html_generator.py"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Pattern to match the fingerprint image tag and its source base64 content
    # It starts with `<img class="fingerprint" src="data:image/png;base64,` and ends with `" alt="fingerprint">`
    # or similar structure
    pattern = r'(<img class="fingerprint" src="data:image/png;base64,)[^"]+(" alt="fingerprint">)'
    
    match = re.search(pattern, content)
    if match:
        print("Match found in html_generator.py!")
        # We need to escape any special backslash characters in clean_b64 if needed, but since it's base64 it only has a-zA-Z0-9+/=
        # So we can safely substitute
        new_content = re.sub(pattern, lambda m: m.group(1) + clean_b64 + m.group(2), content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully replaced base64 string in html_generator.py")
    else:
        print("Pattern not found in html_generator.py!")
        
    # Let's also update cover.html if it exists to keep everything in sync
    cover_path = "e:\\my project\\ALLIA\\FPA\\backend\\app\\processing\\cover.html"
    if os.path.exists(cover_path):
        with open(cover_path, "r", encoding="utf-8") as f:
            cover_content = f.read()
            
        cover_match = re.search(pattern, cover_content)
        if cover_match:
            print("Match found in cover.html!")
            new_cover_content = re.sub(pattern, lambda m: m.group(1) + clean_b64 + m.group(2), cover_content)
            with open(cover_path, "w", encoding="utf-8") as f:
                f.write(new_cover_content)
            print("Successfully replaced base64 string in cover.html")
        else:
            print("Pattern not found in cover.html!")

if __name__ == "__main__":
    main()
