"""Top-level image-processing service used by routers.

Provides a stable API (backward-compatible static methods) while internally
delegating to the new pipeline modules.
"""
from __future__ import annotations

from typing import Any, Optional

import cv2
import numpy as np

from .preprocessing import FingerprintPreprocessor, decode_image, encode_png
from .feature_extractor import FingerprintFeatureExtractor


class ImageProcessingService:
    _extractor: Optional[FingerprintFeatureExtractor] = None

    @classmethod
    def _get_extractor(cls) -> FingerprintFeatureExtractor:
        if cls._extractor is None:
            cls._extractor = FingerprintFeatureExtractor()
        return cls._extractor

    # ---- legacy API kept for current router code ----

    @staticmethod
    def calculate_quality_score(image_data: bytes) -> float:
        """Quality score based on the pre-binarization denoised image.

        We run CLAHE+Gabor+bilateral first (same as the storage pipeline) and
        measure Laplacian sharpness + contrast on that intermediate result.
        This gives a meaningful score that reflects actual ridge clarity.
        """
        try:
            img = decode_image(image_data)
            if img is None:
                return 0.0
            preprocessor = FingerprintPreprocessor()
            stages = preprocessor.preprocess_fingerprint(img)
            denoised = stages["denoised"]   # pre-binarization, good for metrics

            laplacian = cv2.Laplacian(denoised, cv2.CV_64F).var()
            sharpness_score = min(100.0, (laplacian / 300.0) * 100.0)

            mean = float(denoised.mean())
            contrast = float(denoised.std())
            brightness_ok = 50.0 <= mean <= 220.0
            contrast_ok = contrast >= 20.0
            penalty = 0.0 if (brightness_ok and contrast_ok) else 15.0
            return float(max(0.0, sharpness_score - penalty))
        except Exception as exc:  # noqa: BLE001
            print(f"calculate_quality_score: {exc}")
            return 0.0

    @staticmethod
    def normalize_fingerprint(image_data: bytes) -> bytes:
        """Run the full forensic pipeline and return the enhanced grayscale PNG.

        This is what gets stored in MinIO — clean, high-contrast grayscale ridges.
        """
        try:
            img = decode_image(image_data)
            if img is None:
                return image_data
            preprocessor = FingerprintPreprocessor()
            stages = preprocessor.preprocess_fingerprint(img)
            return encode_png(stages["denoised"])
        except Exception as exc:  # noqa: BLE001
            print(f"normalize_fingerprint: {exc}")
            return image_data


    @staticmethod
    def extract_features(image_data: bytes) -> dict[str, Any]:
        """Run the full feature-extraction pipeline. Returns a JSON-serialisable dict."""
        try:
            img = decode_image(image_data)
            if img is None:
                return {}
            features = ImageProcessingService._get_extractor().extract_all_features(img)
            return features.to_dict()
        except Exception as exc:  # noqa: BLE001
            print(f"extract_features: {exc}")
            return {}

    # ---- new high-level API ----

    @staticmethod
    def process_fingerprint(image_data: bytes) -> dict[str, Any]:
        """Full pipeline returning quality + features in one call."""
        result: dict[str, Any] = {
            "quality_score": 0.0,
            "features": {},
            "reject_reason": "Format gambar tidak valid.",
            "debug_images": {}
        }
        img = decode_image(image_data)
        if img is None:
            return result

        try:
            # --- Run preprocessing once ---
            preprocessor = FingerprintPreprocessor()
            stages = preprocessor.preprocess_fingerprint(img)
            denoised = stages["denoised"]

            # --- Extract Scores ---
            laplacian = cv2.Laplacian(denoised, cv2.CV_64F).var()
            blur_score = min(100.0, (laplacian / 300.0) * 100.0)
            
            mean = float(denoised.mean())
            contrast = float(denoised.std())
            brightness_score = 100.0 if 50.0 <= mean <= 220.0 else 40.0
            contrast_score = 100.0 if contrast >= 20.0 else 40.0
            
            center_position_score = stages["scores"]["center_position_score"]
            ridge_texture_score = stages["scores"]["ridge_texture_score"]

            # User formula
            quality_score = (blur_score * 0.25) + (contrast_score * 0.20) + (brightness_score * 0.15) + (center_position_score * 0.25) + (ridge_texture_score * 0.15)
            
            # --- Hard Rejects ---
            reject_reason = None
            if center_position_score < 50:
                reject_reason = "Posisi jari tidak berada di tengah / area sidik jari tidak terdeteksi. Saran: Hadapkan bantalan ujung jari ke kamera dan letakkan di tengah panduan."
                quality_score = min(quality_score, 69.0)
            elif ridge_texture_score < 40:
                reject_reason = "Garis sidik jari tidak terlihat jelas. Saran: Dekatkan jari sedikit atau ubah pencahayaan."
                quality_score = min(quality_score, 69.0)
            elif blur_score < 50:
                reject_reason = "Gambar terlalu buram. Saran: Tahan jari agar fokus kamera dapat menyesuaikan."
                quality_score = min(quality_score, 69.0)
            elif quality_score < 70:
                reject_reason = "Kualitas sidik jari kurang baik. Coba ambil ulang."

            result["quality_score"] = float(quality_score)
            result["reject_reason"] = reject_reason

            # --- Base64 Debug Images ---
            import base64
            def to_b64(img_arr):
                ok, buf = cv2.imencode(".jpg", img_arr)
                if ok:
                    return base64.b64encode(buf).decode("utf-8")
                return ""
                
            result["debug_images"] = {
                "raw_crop": to_b64(stages["gray"]),
                "gabor_image": to_b64(stages["gabor"]),
                "binary_image": to_b64(stages["denoised"]),
                "enhanced_image": to_b64(stages["denoised"])
            }

            # --- Feature extraction on the original image ---
            features = ImageProcessingService._get_extractor().extract_all_features(img)
            result["features"] = features.to_dict()

            # Prefer the feature-extractor's quality score when available, but limit it if we hard rejected
            if features.quality_score > 0 and reject_reason is None:
                result["quality_score"] = features.quality_score

        except Exception as exc:  # noqa: BLE001
            print(f"process_fingerprint: {exc}")
            result["reject_reason"] = f"Error processing image: {exc}"

        return result
