import base64
import os

def main():
    img_path = "e:\\my project\\ALLIA\\FPA\\backend\\result image\\0_default.png"
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        b64_str = base64.b64encode(data).decode("utf-8")
        print(f"Base64 string length for 0_default.png: {len(b64_str)}")
        print(f"Starts with: {b64_str[:120]}")
        
        # Save it to original_b64.txt
        with open("original_b64.txt", "w") as f:
            f.write(b64_str)
        print("Saved base64 of 0_default.png to original_b64.txt")
    else:
        print("0_default.png not found.")

if __name__ == "__main__":
    main()
