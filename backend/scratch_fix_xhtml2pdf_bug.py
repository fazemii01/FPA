import re
import os

def main():
    file_path = "e:\\my project\\ALLIA\\FPA\\backend\\app\\report_engine\\html_generator.py"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Pattern to match:
    # @page:first {
    #     margin: 0;
    # }
    # using double braces since it is formatted
    pattern = r'\s*@page:first\s*\{\{\s*margin:\s*0;\s*\}\}\s*'
    
    match = re.search(pattern, content)
    if match:
        print("Found @page:first in html_generator.py, removing it to fix xhtml2pdf parser bug...")
        new_content = re.sub(pattern, "\n\n", content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully removed @page:first from html_generator.py")
    else:
        print("@page:first pattern not found in html_generator.py or already removed.")
        
    # Let's check cover.html as well
    cover_path = "e:\\my project\\ALLIA\\FPA\\backend\\app\\processing\\cover.html"
    if os.path.exists(cover_path):
        with open(cover_path, "r", encoding="utf-8") as f:
            cover_content = f.read()
            
        # cover.html has single braces because it is raw HTML
        cover_pattern = r'\s*@page:first\s*\{\s*margin:\s*0;\s*\}\s*'
        cover_match = re.search(cover_pattern, cover_content)
        if cover_match:
            print("Found @page:first in cover.html, removing it...")
            new_cover_content = re.sub(cover_pattern, "\n\n", cover_content)
            with open(cover_path, "w", encoding="utf-8") as f:
                f.write(new_cover_content)
            print("Successfully removed @page:first from cover.html")
        else:
            print("@page:first pattern not found in cover.html or already removed.")

if __name__ == "__main__":
    main()
