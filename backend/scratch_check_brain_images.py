import os
import base64

def main():
    convo_id = "3c3b6b90-88fa-44d5-acd0-b5b0c093be10"
    brain_dir = f"C:\\Users\\fazemii01\\.gemini\\antigravity\\brain\\{convo_id}"
    temp_media_dir = os.path.join(brain_dir, ".tempmediaStorage")
    
    directories = [brain_dir, temp_media_dir]
    
    print("--- Inspecting Image Files in Brain & Temp Media Directories ---")
    
    found_any = False
    
    for directory in directories:
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist.")
            continue
            
        print(f"\nScanning directory: {directory}")
        for filename in os.listdir(directory):
            if filename.endswith((".png", ".jpg", ".jpeg")):
                filepath = os.path.join(directory, filename)
                size_bytes = os.path.getsize(filepath)
                
                # We know the corrupted/grayscale ones are:
                # - 108350 bytes (result image/0_default.png)
                # - 292349 / 302390 bytes (which are probably full-page screenshots)
                # - 42097 / 45430 bytes (small ones)
                # The candidate is likely around 144,132 bytes or 137,775 bytes
                print(f"File: {filename} | Size: {size_bytes} bytes")
                
                with open(filepath, "rb") as f:
                    img_data = f.read()
                    
                b64_str = base64.b64encode(img_data).decode("utf-8")
                
                # Save base64 for files that are candidates
                # Let's save base64 for files around 144,132 bytes or 137,775 bytes, or save all of them with prefix
                out_name = f"brain_candidate_b64_{filename.replace('.', '_')}.txt"
                with open(out_name, "w", encoding="utf-8") as out_f:
                    out_f.write(b64_str)
                
                print(f"  -> Generated base64 string (Length: {len(b64_str)}) saved to {out_name}")
                print(f"  -> Base64 Prefix: {b64_str[:60]}...")
                found_any = True
                
    if not found_any:
        print("\nNo image files found in the brain directories.")

if __name__ == "__main__":
    main()
