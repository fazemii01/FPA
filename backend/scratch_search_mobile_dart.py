import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mobile_lib_dir = os.path.join(os.path.dirname(script_dir), "mobile", "lib")
    
    if not os.path.exists(mobile_lib_dir):
        print(f"Error: {mobile_lib_dir} not found.")
        return
        
    keywords = ["cameracontroller", "flashmode", "exposureoffset", "setexposure", "setflash", "torch", "initialize("]
    print(f"Scanning Dart files in {mobile_lib_dir} for keywords: {keywords}...")
    
    match_count = 0
    for root, dirs, files in os.walk(mobile_lib_dir):
        for file in files:
            if file.endswith(".dart"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            line_lower = line.lower()
                            for kw in keywords:
                                if kw in line_lower:
                                    rel_path = os.path.relpath(file_path, mobile_lib_dir)
                                    print(f"[{kw.upper()}] lib/{rel_path}:{line_num} -> {line.strip()}")
                                    match_count += 1
                                    break
                except Exception as e:
                    pass
                    
    print(f"Scan complete. Found {match_count} matches.")

if __name__ == "__main__":
    main()
