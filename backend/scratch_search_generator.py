import os
import re

def main():
    file_path = "app/report_engine/html_generator.py"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
        
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    print("--- Searching html_generator.py ---")
    for idx, line in enumerate(lines):
        if "ring-inner" in line or "fingerprint" in line or "clean_b64" in line:
            print(f"Line {idx+1}: {line.strip()}")

if __name__ == "__main__":
    main()
