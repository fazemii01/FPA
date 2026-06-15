import re
import os

def resolve_vars(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Map of CSS variables to their direct values
    var_map = {
        r'var\(--navy\)': '#1a2456',
        r'var\(--navy-dark\)': '#141d4a',
        r'var\(--orange\)': '#f06a1e',
        r'var\(--teal\)': '#0f9c8e',
        r'var\(--grey\)': '#6b7280',
        r'var\(--page-w\)': '210mm',
        r'var\(--page-h\)': '297mm'
    }
    
    modified = False
    for pattern, value in var_map.items():
        if re.search(pattern, content):
            content = re.sub(pattern, value, content)
            modified = True
            
    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Successfully resolved CSS variables in {os.path.basename(file_path)}")
    else:
        print(f"No CSS variables found to resolve in {os.path.basename(file_path)}")

def main():
    resolve_vars("e:\\my project\\ALLIA\\FPA\\backend\\app\\report_engine\\html_generator.py")
    resolve_vars("e:\\my project\\ALLIA\\FPA\\backend\\app\\processing\\cover.html")

if __name__ == "__main__":
    main()
