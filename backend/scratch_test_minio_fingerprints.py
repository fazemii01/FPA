# Force-load .env first to override any system env vars before importing app config
import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(backend_dir, ".env")
if os.path.exists(dotenv_path):
    with open(dotenv_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                os.environ[key] = val

# Add backend directory to sys.path
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import cv2
import numpy as np
from app.storage.minio_service import MinIOService
from app.processing.feature_extractor import FingerprintFeatureExtractor

def main():
    print("Testing FingerprintFeatureExtractor directly from disk (no monkeypatches)...")
    extractor = FingerprintFeatureExtractor()
    minio_service = MinIOService()
    
    print(f"Listing objects in MinIO bucket '{minio_service.bucket_name}'...")
    try:
        objects = minio_service.client.list_objects(minio_service.bucket_name, prefix="fingerprints/", recursive=True)
        img_objects = [obj.object_name for obj in objects if obj.object_name.lower().endswith(".png")]
        print(f"Found {len(img_objects)} fingerprint images in MinIO.")
        
        if not img_objects:
            print("No fingerprint images found in MinIO.")
            return
            
        # Download and test the first 10 images
        test_count = min(10, len(img_objects))
        print(f"\nTesting first {test_count} images from MinIO:")
        
        for obj_name in img_objects[:test_count]:
            print(f"\nDownloading {obj_name}...")
            try:
                img_data = minio_service.get_fingerprint(obj_name)
                # Decode image
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                
                if img is None:
                    print("  Failed to decode image data.")
                    continue
                    
                features = extractor.extract_all_features(img)
                print(f"  Detected Pattern Type: {features.pattern_type.value}")
                print(f"  Cores found: {len(features.core_points)} at {features.core_points}")
                print(f"  Deltas found: {len(features.delta_points)} at {features.delta_points}")
                print(f"  Ridge Count: {features.ridge_count}")
            except Exception as e:
                print(f"  Error processing {obj_name}: {e}")
                
    except Exception as list_err:
        print(f"Error listing bucket: {list_err}")

if __name__ == "__main__":
    main()
