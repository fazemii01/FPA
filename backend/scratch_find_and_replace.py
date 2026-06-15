import os

def find_and_replace():
    target = "CLICK FINGER CONSULTING"
    replacement = "TAB ALLIA FINGER"
    
    # We will search in backend/ and docs/
    root_dirs = ["backend", "docs", "mobile"]
    
    count = 0
    for root_dir in root_dirs:
        if not os.path.exists(root_dir):
            continue
        for dirpath, _, filenames in os.walk(root_dir):
            # Skip venv and dot directories
            if "venv" in dirpath or ".git" in dirpath or "__pycache__" in dirpath:
                continue
            for filename in filenames:
                # We only want text files
                ext = os.path.splitext(filename)[1].lower()
                if ext not in [".py", ".html", ".css", ".md", ".txt", ".json", ".xml", ".ini", ".bat", ".sh", ".env"]:
                    continue
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    if target.lower() in content.lower():
                        # Case insensitive find and replace
                        import re
                        # We compile a case-insensitive regex for the target
                        pattern = re.compile(re.escape(target), re.IGNORECASE)
                        new_content = pattern.sub(replacement, content)
                        
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        print(f"[REPLACED] in {filepath}")
                        count += 1
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
                    
    print(f"Total files updated: {count}")

if __name__ == "__main__":
    find_and_replace()
