import os
import cv2
import numpy as np
from app.processing.feature_extractor import FingerprintFeatureExtractor, FingerprintFeatures
from app.processing.ridge_enhancement import RidgeEnhancement
import app.processing.feature_extractor as fe_mod

# Define the new smooth, pixel-level orientation method with block averaging
def smooth_estimate_ridge_orientation(self, gray: np.ndarray) -> np.ndarray:
    img = gray.astype(np.float32)
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)

    # Compute local gradient components vx and vy per pixel
    vx = 2.0 * gx * gy
    vy = gx * gx - gy * gy
    
    # 1. Average gradients over a block-sized window to cancel out ridge-frequency oscillations
    vx_avg = cv2.blur(vx, (self.block_size, self.block_size))
    vy_avg = cv2.blur(vy, (self.block_size, self.block_size))
    
    # 2. Smooth vx and vy with a Gaussian filter to make the field continuous
    vx_smooth = cv2.GaussianBlur(vx_avg, (25, 25), 0)
    vy_smooth = cv2.GaussianBlur(vy_avg, (25, 25), 0)

    # Compute theta per-pixel
    theta = 0.5 * np.arctan2(vx_smooth, vy_smooth) + np.pi / 2.0
    return theta

# Define the new poincare singular point detector with mask erosion and larger NMS radius
def smooth_poincare_singular_points(
    orientation: np.ndarray,
    mask: np.ndarray,
    block: int,
    target: float,
    tolerance: float = 0.5,
) -> list[tuple[int, int]]:
    h, w = orientation.shape
    pts: list[tuple[int, int]] = []
    
    # Erode the mask to avoid border/background noise
    if mask is not None:
        kernel = np.ones((25, 25), np.uint8)
        eroded_mask = cv2.erode(mask, kernel)
    else:
        eroded_mask = None
        
    radius = max(2, block // 4)
    # 8-neighbour ring offsets (clockwise)
    ring = [
        (-radius, -radius), (-radius, 0), (-radius, radius),
        (0, radius), (radius, radius), (radius, 0),
        (radius, -radius), (0, -radius),
    ]
    for y in range(radius, h - radius, max(1, block // 2)):
        for x in range(radius, w - radius, max(1, block // 2)):
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
                
    # Return non-max suppressed points with a larger radius (block * 2.5) to filter out duplicate cluster points
    return fe_mod._non_max_suppress(pts, radius=int(block * 2.5))

def main():
    print("Monkeypatching RidgeEnhancement and FeatureExtractor with orientation smoothing and boundary erosion...")
    RidgeEnhancement.estimate_ridge_orientation = smooth_estimate_ridge_orientation
    fe_mod._poincare_singular_points = smooth_poincare_singular_points
    
    extractor = FingerprintFeatureExtractor()
    
    # Search for image files in backend directory
    img_extensions = [".png", ".jpg", ".jpeg"]
    found_images = []
    
    for root, dirs, files in os.walk("backend"):
        if "venv" in root or ".git" in root or "__pycache__" in root:
            continue
        for file in files:
            if os.path.splitext(file)[1].lower() in img_extensions:
                if file.startswith("log_candidate") or file.startswith("brain_candidate"):
                    continue
                filepath = os.path.join(root, file)
                found_images.append(filepath)
                
    print(f"Found {len(found_images)} images to test:")
    
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
