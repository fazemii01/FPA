import os

def main():
    search_term = "CLICK"
    print(f"Searching for case-insensitive occurrences of '{search_term}' in all workspace files...")
    
    # We will search the entire workspace e:\my project\ALLIA\FPA
    workspace_root = "e:\\my project\\ALLIA\\FPA"
    
    matches = []
    for root, dirs, files in os.walk(workspace_root):
        # Skip standard ignore dirs to avoid search bloat, but search everything else
        if any(ignored in root for ignored in [".git", "venv", ".pytest_cache", "__pycache__", ".claude"]):
            continue
        for file in files:
            filepath = os.path.join(root, file)
            # Skip binary file formats (like .pdf, .db, .png) to avoid binary noise
            ext = os.path.splitext(file)[1].lower()
            if ext in [".pdf", ".db", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".xlsx"]:
                continue
                
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        if search_term.lower() in line.lower():
                            matches.append((filepath, line_num, line.strip()))
            except Exception as e:
                print(f"Could not read {filepath}: {e}")
                
    if matches:
        print(f"Found {len(matches)} matches:")
        for path, line_num, content in matches:
            print(f"{path}:{line_num}: {content}")
    else:
        print("No matches found.")

if __name__ == "__main__":
    main()
