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
from app.processing.ridge_enhancement import RidgeEnhancement
import app.processing.feature_extractor as fe_mod

# Custom estimator with custom box and gaussian sizes
def custom_estimate_ridge_orientation(gray: np.ndarray, box_size: int, g_size: int) -> np.ndarray:
    img = gray.astype(np.float32)
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)

    vx = 2.0 * gx * gy
    vy = gx * gx - gy * gy
    
    vx_avg = cv2.blur(vx, (box_size, box_size))
    vy_avg = cv2.blur(vy, (box_size, box_size))
    
    vx_smooth = cv2.GaussianBlur(vx_avg, (g_size, g_size), 0)
    vy_smooth = cv2.GaussianBlur(vy_avg, (g_size, g_size), 0)

    theta = 0.5 * np.arctan2(vx_smooth, vy_smooth) + np.pi / 2.0
    return theta

# Custom Poincaré detector
def custom_poincare_singular_points(
    orientation: np.ndarray,
    mask: np.ndarray,
    block_size: int,
    target: float,
    tolerance: float = 0.5,
) -> list[tuple[int, int]]:
    h, w = orientation.shape
    pts: list[tuple[int, int]] = []
    
    # Erode mask relative to block size
    if mask is not None:
        e_size = max(5, int(block_size * 1.5))
        kernel = np.ones((e_size, e_size), np.uint8)
        eroded_mask = cv2.erode(mask, kernel)
    else:
        eroded_mask = None
        
    radius = 3
    ring = [
        (-radius, -radius), (-radius, 0), (-radius, radius),
        (0, radius), (radius, radius), (radius, 0),
        (radius, -radius), (0, -radius),
    ]
    step = 2
    for y in range(radius, h - radius, step):
        for x in range(radius, w - radius, step):
            if eroded_mask is not None and eroded_mask[y, x] == 0:
                continue
            angles = [orientation[y + dy, x + dx] for dy, dx in ring]
            total = 0.0
            for i in range(len(angles)):
                d = angles[(i + 1) % len(angles)] - angles[i]
                if d > np.pi / 2:
                    d -= np.pi
                elif d < -np.pi / 2:
                    d += np.pi
                total += d
            if abs(total - target) < tolerance:
                pts.append((int(x), int(y)))
                
    nms_rad = int(block_size * 2.5)
    return fe_mod._non_max_suppress(pts, radius=nms_rad)

def main():
    minio_service = MinIOService()
    
    print(f"Listing objects in MinIO bucket '{minio_service.bucket_name}'...")
    try:
        objects = minio_service.client.list_objects(minio_service.bucket_name, prefix="fingerprints/", recursive=True)
        img_objects = [obj.object_name for obj in objects if obj.object_name.lower().endswith(".png")]
        
        if not img_objects:
            print("No images found.")
            return
            
        # We will test the first 3 images
        test_images = img_objects[:3]
        
        # Download images once to cache them
        images = []
        for obj_name in test_images:
            print(f"Downloading {obj_name}...")
            img_data = minio_service.get_fingerprint(obj_name)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                extractor = FingerprintFeatureExtractor()
                steps = extractor.preprocessor.preprocess_fingerprint(img)
                enhanced = steps["enhanced"]
                mask = extractor.segmentation.create_segmentation_mask(enhanced)
                images.append((obj_name, enhanced, mask))
                
        # Fine-grained parameter sweep
        sweeps = [
            (8, 9),
            (10, 11),
            (12, 13),
            (14, 15),
            (16, 17)
        ]
        
        print("\n--- Starting Fine-Grained Parameter Sweep ---")
        for box, gauss in sweeps:
            print(f"\n==========================================")
            print(f"Box Blur Size: {box}x{box} | Gaussian Blur Size: {gauss}x{gauss}")
            print(f"==========================================")
            
            for obj_name, enhanced, mask in images:
                # Calculate orientation
                orient = custom_estimate_ridge_orientation(enhanced, box, gauss)
                
                # Detect singular points (using box size as the block_size reference for NMS and erosion)
                cores = custom_poincare_singular_points(orient, mask, box, target=+np.pi)
                deltas = custom_poincare_singular_points(orient, mask, box, target=-np.pi)
                
                # Classify pattern
                stability = FingerprintFeatureExtractor.measure_orientation_stability(orient, mask)
                pattern = FingerprintFeatureExtractor.detect_pattern_type(cores, deltas, stability)
                
                print(f"\nImage: {obj_name}")
                print(f"  Cores found: {len(cores)} at {cores}")
                print(f"  Deltas found: {len(deltas)} at {deltas}")
                print(f"  Detected Pattern Type: {pattern.value}")
                
    except Exception as list_err:
        print(f"Error listing bucket or running test: {list_err}")

if __name__ == "__main__":
    main()
