import numpy as np
from app.processing.preprocessing import FingerprintPreprocessor

def test_preprocessing():
    print("Initializing preprocessor...")
    preprocessor = FingerprintPreprocessor()
    
    print("Generating mock fingerprint image (512x512)...")
    # Generate a simple mock fingerprint: circular concentric circles (like a simple whorl pattern)
    # on a light skin background (value ~200) with dark ridges (value ~80)
    image = np.full((512, 512), 200, dtype=np.uint8)
    cy, cx = 256, 256
    for r in range(20, 240, 20):
        # Draw some dark circles (representing ridges)
        for dr in range(-3, 4):
            # Draw circles using simple pixel calculation
            for theta in np.linspace(0, 2*np.pi, 360):
                x = int(cx + (r + dr) * np.cos(theta))
                y = int(cy + (r + dr) * np.sin(theta))
                if 0 <= x < 512 and 0 <= y < 512:
                    image[y, x] = 80

    print("Running preprocess_fingerprint pipeline...")
    stages = preprocessor.preprocess_fingerprint(image)
    
    print("\n--- Preprocessing Output Check ---")
    keys = ["gray", "resized", "enhanced", "gabor", "denoised", "binarized", "cleaned", "enhanced_binary", "scores"]
    for key in keys:
        present = key in stages
        print(f"Key '{key}': {'PASSED' if present else 'FAILED'}")
        assert present, f"Key '{key}' is missing from output!"

    scores = stages["scores"]
    print(f"\nQuality scores computed successfully:")
    print(f"  Center Position Score: {scores['center_position_score']:.2f}")
    print(f"  Ridge Texture Score:   {scores['ridge_texture_score']:.2f}")
    
    print("\n[SUCCESS] FingerprintPreprocessor tests passed completely!")

if __name__ == "__main__":
    test_preprocessing()
