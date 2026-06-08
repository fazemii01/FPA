"""Fingerprint preprocessing — forensic enhancement pipeline.

Pipeline (produces crisp black-ridge-on-white image like an ink stamp):
  1. Grayscale conversion
  2. Resize to 512×512 (normalise sensor differences)
  3. CLAHE  (contrast-limited adaptive histogram equalisation)
  4. Gabor filter bank (8 orientations) — ridge enhancement
  5. Bilateral denoising (edge-preserving)
  6. Sauvola adaptive thresholding — binary output
  7. Morphological closing — fill small ridge gaps
  8. Polarity normalisation — ensure ridges are black (0) on white (255)

References: FR-07 in PRD.
"""
from __future__ import annotations

import cv2
import numpy as np


TARGET_SIZE = 512   # pixels — stored image is always 512×512


class FingerprintPreprocessor:
    """Operates on grayscale numpy arrays (uint8)."""

    def __init__(
        self,
        clahe_clip_limit: float = 5.0,
        clahe_tile_size: int = 8,
        bilateral_d: int = 7,
        bilateral_sigma_color: float = 50.0,
        bilateral_sigma_space: float = 50.0,
        adaptive_block_size: int = 41,
        adaptive_c: float = 4.0,
    ) -> None:
        self.clahe_clip_limit = clahe_clip_limit
        self.clahe_tile_size = clahe_tile_size
        self.bilateral_d = bilateral_d
        self.bilateral_sigma_color = bilateral_sigma_color
        self.bilateral_sigma_space = bilateral_sigma_space
        self.adaptive_block_size = adaptive_block_size
        self.adaptive_c = adaptive_c

    # ── helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        if image.ndim == 2:
            return image
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def resize_to_target(image: np.ndarray, size: int = TARGET_SIZE) -> np.ndarray:
        """Resize to size×size keeping aspect ratio, pad with white if needed."""
        h, w = image.shape[:2]
        scale = size / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        # Pad to square with white (255)
        canvas = np.full((size, size), 255, dtype=np.uint8)
        y_off = (size - new_h) // 2
        x_off = (size - new_w) // 2
        canvas[y_off:y_off + new_h, x_off:x_off + new_w] = resized
        return canvas

    # ── pipeline steps ─────────────────────────────────────────────────────

    @staticmethod
    def recenter_fingerprint(gray: np.ndarray) -> np.ndarray:
        # Simple threshold to find foreground (finger is darker than white bg)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return gray
            
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        
        # Crop to bounding box
        cropped = gray[y:y+h, x:x+w]
        
        # Pad to square
        size = max(w, h)
        padded = np.full((size, size), 255, dtype=np.uint8)
        x_off = (size - w) // 2
        y_off = (size - h) // 2
        padded[y_off:y_off+h, x_off:x_off+w] = cropped
        return padded

    @staticmethod
    def apply_gamma_correction(image: np.ndarray, gamma: float = 0.5) -> np.ndarray:
        """Apply gamma correction to recover detail from overexposed images.

        gamma < 1.0 darkens bright areas (recovers blown-out ridge valleys).
        gamma > 1.0 brightens dark areas (recovers underexposed images).
        Build a lookup table for speed (256-entry, avoids per-pixel pow()).
        """
        inv_gamma = 1.0 / gamma
        table = np.array(
            [((i / 255.0) ** inv_gamma) * 255 for i in range(256)],
            dtype=np.uint8,
        )
        return cv2.LUT(image, table)

    def apply_clahe(self, image: np.ndarray) -> np.ndarray:
        clahe = cv2.createCLAHE(
            clipLimit=self.clahe_clip_limit,
            tileGridSize=(self.clahe_tile_size, self.clahe_tile_size),
        )
        return clahe.apply(image)

    def apply_gabor_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Apply a bank of Gabor filters at 8 orientations to enhance ridges.

        Gabor filters are oriented band-pass filters tuned to fingerprint ridge
        frequency (~500 µm spacing at 500 dpi → frequency ≈ 0.1 cycles/px at 512 px).
        """
        ksize = 21          # kernel size (pixels)
        sigma = 4.0         # Gaussian envelope width
        frequency = 0.1     # ridge frequency in cycles/pixel
        gamma = 0.5         # aspect ratio

        img_float = image.astype(np.float32)
        accumulator = np.zeros_like(img_float)

        for angle_deg in range(0, 180, 22):   # 8 orientations: 0°…157°
            theta = np.deg2rad(angle_deg)
            kernel = cv2.getGaborKernel(
                ksize=(ksize, ksize),
                sigma=sigma,
                theta=theta,
                lambd=1.0 / frequency,
                gamma=gamma,
                psi=0,
                ktype=cv2.CV_32F,
            )
            kernel /= kernel.sum() if kernel.sum() != 0 else 1.0
            filtered = cv2.filter2D(img_float, cv2.CV_32F, kernel)
            accumulator = np.maximum(accumulator, filtered)

        # Normalise back to [0, 255] uint8
        cv2.normalize(accumulator, accumulator, 0, 255, cv2.NORM_MINMAX)
        return accumulator.astype(np.uint8)

    def denoise_bilateral(self, image: np.ndarray) -> np.ndarray:
        return cv2.bilateralFilter(
            image,
            d=self.bilateral_d,
            sigmaColor=self.bilateral_sigma_color,
            sigmaSpace=self.bilateral_sigma_space,
        )

    def apply_adaptive_threshold(self, image: np.ndarray) -> np.ndarray:
        """Gaussian adaptive thresholding matching tap finger's high-fidelity output.

        Uses THRESH_BINARY_INV so white ridges (255) are foreground and black valleys (0) are background.
        This enables proper morphological operations on the ridges.
        """
        block_size = self.adaptive_block_size
        if block_size % 2 == 0:
            block_size += 1
            
        out_inv = cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            block_size,
            self.adaptive_c,
        )
        return out_inv

    def apply_morphological_cleanup(self, binary: np.ndarray) -> np.ndarray:
        """Close small gaps in ridges with a tiny elliptic structuring element."""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        # closing = dilation then erosion — fills small holes in ridges
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
        return closed

    @staticmethod
    def ensure_black_ridges_on_white(binary: np.ndarray) -> np.ndarray:
        """Ensure ridges are black (0) on white (255) background.

        Some images come in inverted (white ridges on black). If the mean pixel
        value is below 128 the image is already mostly dark → invert it.
        """
        if float(binary.mean()) < 128:
            return cv2.bitwise_not(binary)
        return binary

    # ── main entry point ───────────────────────────────────────────────────

    def preprocess_fingerprint(self, image: np.ndarray) -> dict:
        """Full forensic enhancement pipeline.

        Returns dict with intermediate stages for debugging and the final
        enhanced binary image under the key ``enhanced_binary``.
        """
        gray = self.to_grayscale(image)

        # 1. The mobile app already crops the image tightly to the guide ROI.
        # We bypass recenter_fingerprint to prevent it from accidentally cropping 
        # valid ridges due to flash shadows.
        # recentered = self.recenter_fingerprint(gray)

        # 2. Resize to 512x512 (resize_to_target automatically pads it to a square with white margins)
        resized = self.resize_to_target(gray, TARGET_SIZE)

        # --- Overexposure guard ---
        mean_brightness = float(resized.mean())
        if mean_brightness > 210:
            resized = self.apply_gamma_correction(resized, gamma=0.45)
        elif mean_brightness < 60:
            resized = self.apply_gamma_correction(resized, gamma=1.8)

        # 3. Enhance & Denoise
        clahe_img = self.apply_clahe(resized)
        denoised_base = self.denoise_bilateral(clahe_img)
        
        # Contrast stretching: clip 2% and 98% percentiles and stretch to [0, 255]
        p2, p98 = np.percentile(denoised_base, (2, 98))
        denoised_stretched = np.clip(denoised_base, p2, p98)
        denoised_stretched = ((denoised_stretched - p2) / (p98 - p2 + 1e-6) * 255.0).astype(np.uint8)

        # Unsharp masking to make the ridge lines bold and sharp
        blurred = cv2.GaussianBlur(denoised_stretched, (0, 0), 2.0)
        sharpened = cv2.addWeighted(denoised_stretched, 2.0, blurred, -1.0, 0)

        # 2x2 grayscale erosion to thicken the dark ridges (valleys are white, ridges are black)
        kernel_2x2 = np.ones((2, 2), np.uint8)
        eroded = cv2.erode(sharpened, kernel_2x2, iterations=1)

        # Apply midtone darkening curve (y = x^1.8 / 255^0.8) to make ridges blacker/bolder
        lut_dark = np.array([((i / 255.0) ** 1.8) * 255 for i in range(256)], dtype=np.uint8)
        darkened = cv2.LUT(eroded, lut_dark)

        # Final contrast stretching to keep background white and ridges high contrast
        p2, p98 = np.percentile(darkened, (2, 98))
        denoised = np.clip(darkened, p2, p98)
        denoised = ((denoised - p2) / (p98 - p2 + 1e-6) * 255.0).astype(np.uint8)
        
        # We still run Gabor internally only to compute the ridge texture score
        gabor_img = self.apply_gabor_enhancement(clahe_img)

        # 4. Center Position Score (Check darkest ridge pixels in 3 vertical zones)
        w = TARGET_SIZE
        left_zone = gabor_img[:, 0:w//3].sum()
        center_zone = gabor_img[:, w//3:2*w//3].sum()
        right_zone = gabor_img[:, 2*w//3:w].sum()
        total = left_zone + center_zone + right_zone + 1e-6
        center_ratio = center_zone / total
        
        # if perfectly balanced, center_ratio is 0.33. If ridge is centered, it's > 0.4
        # map 0.33 -> 50, 0.5 -> 100
        center_position_score = min(100.0, max(0.0, (center_ratio - 0.25) * 400.0))
        
        # 5. Ridge Texture Score (Gabor response strength)
        ridge_texture_score = min(100.0, (float(gabor_img.mean()) / 128.0) * 100.0)

        # 6. Finalize Binary (Gaussian adaptive threshold on the clean denoised CLAHE image)
        # Using THRESH_BINARY_INV so white ridges (255) are foreground and black valleys (0) are background
        binarized_inv = self.apply_adaptive_threshold(denoised)
        
        # Morphological cleanup on the white ridges (255) foreground image:
        # Closing (cv2.MORPH_CLOSE) closes small gaps/holes in the ridges (foreground)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned_inv = cv2.morphologyEx(binarized_inv, cv2.MORPH_CLOSE, kernel)
        
        # Invert to standard black ridges on white background
        final = cv2.bitwise_not(cleaned_inv)
        binarized = cv2.bitwise_not(binarized_inv)
        cleaned = final

        return {
            "gray": gray,
            "recentered": gray,
            "resized": resized,
            "enhanced": clahe_img,
            "gabor": gabor_img,
            "denoised": denoised,
            "binarized": binarized,
            "cleaned": cleaned,
            "enhanced_binary": final,
            "scores": {
                "center_position_score": center_position_score,
                "ridge_texture_score": ridge_texture_score
            }
        }



def decode_image(image_bytes: bytes) -> np.ndarray | None:
    arr = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def encode_png(image: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", image)
    if not ok:
        raise RuntimeError("Failed to encode PNG")
    return buf.tobytes()
