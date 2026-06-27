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

# Revert estimate_ridge_orientation to the original block-wise calculation
def original_estimate_ridge_orientation(self, gray: np.ndarray) -> np.ndarray:
    h, w = gray.shape
    bs = self.block_size
    orient = np.zeros((h, w), dtype=np.float32)
    img = gray.astype(np.float32)
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)

    vx = 2.0 * gx * gy
    vy = gx * gx - gy * gy

    vx_smooth = cv2.GaussianBlur(vx, (15, 15), 0)
    vy_smooth = cv2.GaussianBlur(vy, (15, 15), 0)

    for y in range(0, h, bs):
        for x in range(0, w, bs):
            vx_blk = vx_smooth[y : y + bs, x : x + bs]
            vy_blk = vy_smooth[y : y + bs, x : x + bs]
            if vx_blk.size == 0:
                continue
            v_x = float(np.sum(vx_blk))
            v_y = float(np.sum(vy_blk))
            theta = 0.5 * np.arctan2(v_x, v_y) + np.pi / 2.0
            orient[y : y + bs, x : x + bs] = theta
    return orient

# Poincaré detector with mask erosion and sweepable NMS radius
def sweep_detect_singular_points(orientation: np.ndarray, mask: np.ndarray, block_size: int, target: float, nms_radius: int) -> list[tuple[int, int]]:
    # Erode mask heavily to avoid border noise
    if mask is not None:
        kernel = np.ones((25, 25), np.uint8)
        eroded_mask = cv2.erode(mask, kernel)
    else:
        eroded_mask = None
        
    pts = fe_mod._poincare_singular_points(orientation, eroded_mask, block_size, target)
    return fe_mod._non_max_suppress(pts, radius=nms_radius)

def main():
    print("Testing original block-wise filter with mask erosion + sweep of NMS radius...")
    RidgeEnhancement.estimate_ridge_orientation = original_estimate_ridge_orientation
    
    extractor = FingerprintFeatureExtractor()
    minio_service = MinIOService()
    
    try:
        objects = minio_service.client.list_objects(minio_service.bucket_name, prefix="fingerprints/", recursive=True)
        img_objects = [obj.object_name for obj in objects if obj.object_name.lower().endswith(".png")]
        
        if not img_objects:
            print("No images found.")
            return
            
        test_images = img_objects[:3]
        images = []
        for obj_name in test_images:
            print(f"Downloading {obj_name}...")
            img_data = minio_service.get_fingerprint(obj_name)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                steps = extractor.preprocessor.preprocess_fingerprint(img)
                enhanced = steps["enhanced"]
                mask = extractor.segmentation.create_segmentation_mask(enhanced)
                images.append((obj_name, enhanced, mask))
                
        nms_radii = [32, 64, 96, 128]
        
        for radius in nms_radii:
            print(f"\n==========================================")
            print(f"NMS Radius: {radius} pixels")
            print(f"==========================================")
            
            for obj_name, enhanced, mask in images:
                orient = extractor.ridge.estimate_ridge_orientation(enhanced)
                cores = sweep_detect_singular_points(orient, mask, extractor.ridge.block_size, target=np.pi, nms_radius=radius)
                deltas = sweep_detect_singular_points(orient, mask, extractor.ridge.block_size, target=-np.pi, nms_radius=radius)
                
                stability = extractor.measure_orientation_stability(orient, mask)
                pattern = extractor.detect_pattern_type(cores, deltas, stability)
                
                print(f"\nImage: {obj_name}")
                print(f"  Cores found: {len(cores)} at {cores}")
                print(f"  Deltas found: {len(deltas)} at {deltas}")
                print(f"  Detected Pattern Type: {pattern.value}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
