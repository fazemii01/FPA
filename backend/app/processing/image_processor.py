import cv2
import numpy as np
from PIL import Image
import io


class ImageProcessingService:
    @staticmethod
    def calculate_quality_score(image_data: bytes) -> float:
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            
            if img is None:
                return 0.0
            
            laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
            quality_score = min(100.0, (laplacian_var / 500.0) * 100)
            
            return float(max(0.0, quality_score))
        except Exception as e:
            print(f"Error calculating quality score: {e}")
            return 0.0
    
    @staticmethod
    def normalize_fingerprint(image_data: bytes) -> bytes:
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            
            if img is None:
                return image_data
            
            normalized = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
            _, normalized = cv2.threshold(normalized, 127, 255, cv2.THRESH_BINARY)
            
            _, buffer = cv2.imencode('.png', normalized)
            return buffer.tobytes()
        except Exception as e:
            print(f"Error normalizing fingerprint: {e}")
            return image_data
    
    @staticmethod
    def extract_features(image_data: bytes) -> dict:
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            
            if img is None:
                return {}
            
            edges = cv2.Canny(img, 100, 200)
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            return {
                "contour_count": len(contours),
                "image_shape": img.shape,
                "edge_density": np.sum(edges > 0) / edges.size
            }
        except Exception as e:
            print(f"Error extracting features: {e}")
            return {}
