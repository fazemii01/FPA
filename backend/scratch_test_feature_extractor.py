import os
import cv2
from app.processing.feature_extractor import FingerprintFeatureExtractor

def main():
    print("Testing Feature Extractor on available raw images...")
    
    # Check if there are any candidate image files or folders in backend
    # E.g., 'example finger path', 'result image', or image files
    extractor = FingerprintFeatureExtractor()
    
    # We will search for image files in backend directory
    img_extensions = [".png", ".jpg", ".jpeg"]
    found_images = []
    
    for root, dirs, files in os.walk("backend"):
        if "venv" in root or ".git" in root or "__pycache__" in root:
            continue
        for file in files:
            if os.path.splitext(file)[1].lower() in img_extensions:
                # Skip compiled PDF/system files
                if file.startswith("log_candidate") or file.startswith("brain_candidate"):
                    continue
                filepath = os.path.join(root, file)
                found_images.append(filepath)
                
    print(f"Found {len(found_images)} images to test:")
    for path in found_images[:10]:
        print(f"  {path}")
        
    for path in found_images[:5]:
        print(f"\nProcessing {path}...")
        try:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                print("  Failed to load image.")
                continue
            features = extractor.extract_all_features(img)
            print(f"  Detected Pattern Type: {features.pattern_type.value}")
            print(f"  Cores found: {len(features.core_points)} at {features.core_points}")
            print(f"  Deltas found: {len(features.delta_points)} at {features.delta_points}")
            print(f"  Ridge Count: {features.ridge_count}")
        except Exception as e:
            print(f"  Error processing image: {e}")

if __name__ == "__main__":
    main()
