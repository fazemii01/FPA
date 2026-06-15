import os
import re

def main():
    file_path = "app/report_engine/html_generator.py"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    print("--- Checking Style Selectors in html_generator.py ---")
    
    # Check for .page selector
    page_matches = re.findall(r'(\.page\s*\{\{.*?\}\})', content, re.DOTALL)
    print(f"Found {len(page_matches)} occurrences of .page style block:")
    for idx, match in enumerate(page_matches):
        print(f"Match {idx+1}:\n{match.strip()}\n")
        
    # Check for .report-page selector
    report_page_matches = re.findall(r'(\.report-page\s*\{\{.*?\}\})', content, re.DOTALL)
    print(f"Found {len(report_page_matches)} occurrences of .report-page style block:")
    for idx, match in enumerate(report_page_matches):
        print(f"Match {idx+1}:\n{match.strip()}\n")

    # Check for .page-cover selector
    page_cover_matches = re.findall(r'(\.page-cover\s*\{\{.*?\}\})', content, re.DOTALL)
    print(f"Found {len(page_cover_matches)} occurrences of .page-cover style block:")
    for idx, match in enumerate(page_cover_matches):
        print(f"Match {idx+1}:\n{match.strip()}\n")

if __name__ == "__main__":
    main()
