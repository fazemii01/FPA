import os
import base64
from PIL import Image
import io

def inspect_image_data(img_bytes, label):
    try:
        img = Image.open(io.BytesIO(img_bytes))
        width, height = img.size
        mode = img.mode
        
        # Calculate some color statistics to identify grayscale vs blue color
        # Convert to RGB to get channel stats
        rgb_img = img.convert("RGB")
        pixels = list(rgb_img.getdata())
        
        total_pixels = len(pixels)
        r_sum = g_sum = b_sum = 0
        non_white_gray_pixels = 0
        blue_heavy_pixels = 0
        
        for r, g, b in pixels:
            r_sum += r
            g_sum += g
            b_sum += b
            # Check if it's not white/black/gray (tolerance of 5)
            if not (abs(r - g) < 5 and abs(g - b) < 5 and abs(r - b) < 5):
                non_white_gray_pixels += 1
                if b > r + 20 and b > g + 20:
                    blue_heavy_pixels += 1
                    
        avg_r = r_sum / total_pixels
        avg_g = g_sum / total_pixels
        avg_b = b_sum / total_pixels
        
        print(f"[{label}]")
        print(f"  Dimensions: {width}x{height} | Mode: {mode}")
        print(f"  Avg Color (RGB): ({avg_r:.1f}, {avg_g:.1f}, {avg_b:.1f})")
        print(f"  Non-grayscale pixels: {non_white_gray_pixels} ({non_white_gray_pixels/total_pixels*100:.1f}%)")
        print(f"  Blue-heavy pixels: {blue_heavy_pixels} ({blue_heavy_pixels/total_pixels*100:.1f}%)")
        return {
            "label": label,
            "width": width,
            "height": height,
            "is_color": non_white_gray_pixels > 100,
            "is_blue": blue_heavy_pixels > 100,
            "size": len(img_bytes)
        }
    except Exception as e:
        print(f"[{label}] Error: {e}")
        return None

def main():
    print("--- Inspecting Image Candidates for Color/Dimensions ---")
    
    # Files to inspect
    files_to_check = [
        "original_b64.txt",
        "log_candidate_b64_0.txt",
        "brain_candidate_b64_media__1781081434304_png.txt",
        "brain_candidate_b64_media__1781236002239_png.txt"
    ]
    
    for filename in files_to_check:
        if not os.path.exists(filename):
            print(f"File {filename} not found.")
            continue
            
        with open(filename, "r", encoding="utf-8") as f:
            b64_str = f.read().strip()
            
        try:
            if "," in b64_str:
                b64_str = b64_str.split(",")[1]
            img_bytes = base64.b64decode(b64_str)
            inspect_image_data(img_bytes, filename)
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    main()
