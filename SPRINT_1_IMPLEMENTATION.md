# Sprint 1: Enhanced Image Processing Implementation Guide
**Duration**: 2 weeks (May 19 - June 2, 2026)  
**Goal**: Complete OpenCV fingerprint processing pipeline  
**Status**: Ready to Start

---

## Overview

This sprint implements a comprehensive image processing pipeline that transforms raw fingerprint images into processed, enhanced images with extracted features. This is the foundation for the scoring engine.

---

## Architecture Diagram

```
Raw Fingerprint Image (JPG/PNG)
         ↓
    [PREPROCESSING]
    - Normalize
    - CLAHE enhancement
    - Bilateral denoising
    - Sauvola thresholding
         ↓
    [SEGMENTATION]
    - Detect fingerprint region
    - Extract ROI
    - Create mask
         ↓
    [RIDGE ENHANCEMENT]
    - Estimate orientation
    - Estimate frequency
    - Apply Gabor filters
         ↓
    [THRESHOLDING & MORPHOLOGY]
    - Adaptive thresholding
    - Morphological operations
    - Cleanup artifacts
         ↓
    [SKELETONIZATION]
    - Zhang-Suen thinning
    - Ridge skeleton extraction
         ↓
    [FEATURE EXTRACTION]
    - Pattern type (whorl/loop/arch)
    - Ridge count
    - Core/delta points
    - Minutiae (endings/bifurcations)
    - Ridge density
    - Orientation stability
         ↓
    Processed Image + Features JSON
```

---

## Task Breakdown

### Task 1.1: Create Preprocessing Module (Days 1-2)

**File**: `backend/app/processing/preprocessing.py`

**Purpose**: Enhance image contrast and reduce noise

**Implementation**:

```python
import cv2
import numpy as np
from typing import Tuple

class FingerprintPreprocessor:
    """Preprocessing pipeline for fingerprint images"""
    
    @staticmethod
    def apply_clahe(image: np.ndarray, clip_limit: float = 2.0, 
                    tile_size: int = 8) -> np.ndarray:
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        
        Args:
            image: Grayscale image
            clip_limit: Contrast limit (1.0-4.0)
            tile_size: Size of grid tiles (8-16)
        
        Returns:
            Enhanced image
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, 
                                tileGridSize=(tile_size, tile_size))
        return clahe.apply(image)
    
    @staticmethod
    def denoise_bilateral(image: np.ndarray, diameter: int = 9,
                         sigma_color: float = 75, 
                         sigma_space: float = 75) -> np.ndarray:
        """
        Apply bilateral filtering for edge-preserving denoising
        
        Args:
            image: Input image
            diameter: Diameter of pixel neighborhood
            sigma_color: Filter sigma in the color space
            sigma_space: Filter sigma in the coordinate space
        
        Returns:
            Denoised image
        """
        return cv2.bilateralFilter(image, diameter, sigma_color, sigma_space)
    
    @staticmethod
    def apply_sauvola_threshold(image: np.ndarray, window_size: int = 25,
                               k: float = 0.2) -> np.ndarray:
        """
        Apply Sauvola adaptive thresholding
        
        Args:
            image: Input image
            window_size: Size of local window
            k: Parameter controlling threshold value
        
        Returns:
            Binary image
        """
        # Convert to float
        img_float = image.astype(np.float32)
        
        # Calculate local mean
        mean = cv2.blur(img_float, (window_size, window_size))
        
        # Calculate local standard deviation
        sqr_mean = cv2.blur(img_float ** 2, (window_size, window_size))
        std = np.sqrt(np.maximum(sqr_mean - mean ** 2, 0))
        
        # Calculate threshold
        threshold = mean * (1 + k * (std / 128 - 1))
        
        # Apply threshold
        binary = np.where(img_float >= threshold, 255, 0)
        
        return binary.astype(np.uint8)
    
    @staticmethod
    def preprocess_fingerprint(image: np.ndarray) -> np.ndarray:
        """
        Complete preprocessing pipeline
        
        Args:
            image: Raw fingerprint image
        
        Returns:
            Preprocessed binary image
        """
        # 1. Convert to grayscale if needed
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. Normalize intensity
        image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
        
        # 3. Apply CLAHE for contrast enhancement
        image = FingerprintPreprocessor.apply_clahe(image, clip_limit=2.0)
        
        # 4. Denoise with bilateral filter
        image = FingerprintPreprocessor.denoise_bilateral(image)
        
        # 5. Apply Sauvola thresholding
        image = FingerprintPreprocessor.apply_sauvola_threshold(image)
        
        return image
```

**Tests**:

```python
# File: backend/tests/test_preprocessing.py

import pytest
import cv2
import numpy as np
from app.processing.preprocessing import FingerprintPreprocessor

def test_clahe_enhancement():
    """Test CLAHE improves contrast"""
    # Create test image with low contrast
    image = np.ones((256, 256), dtype=np.uint8) * 128
    image[50:200, 50:200] = 100
    
    enhanced = FingerprintPreprocessor.apply_clahe(image)
    
    assert enhanced.shape == image.shape
    assert enhanced.dtype == np.uint8
    assert np.std(enhanced) > np.std(image)  # Contrast increased

def test_bilateral_denoising():
    """Test bilateral filtering preserves edges"""
    # Create image with noise
    image = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
    
    denoised = FingerprintPreprocessor.denoise_bilateral(image)
    
    assert denoised.shape == image.shape
    assert denoised.dtype == np.uint8

def test_sauvola_threshold():
    """Test Sauvola thresholding produces binary image"""
    image = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
    
    binary = FingerprintPreprocessor.apply_sauvola_threshold(image)
    
    assert binary.shape == image.shape
    assert np.all((binary == 0) | (binary == 255))  # Binary

def test_complete_preprocessing():
    """Test complete preprocessing pipeline"""
    # Create synthetic fingerprint
    image = np.zeros((256, 256), dtype=np.uint8)
    cv2.circle(image, (128, 128), 100, 200, 5)
    
    processed = FingerprintPreprocessor.preprocess_fingerprint(image)
    
    assert processed.shape == image.shape
    assert np.all((processed == 0) | (processed == 255))
```

---

### Task 1.2: Create Segmentation Module (Days 2-3)

**File**: `backend/app/processing/segmentation.py`

**Purpose**: Detect and extract fingerprint region

```python
import cv2
import numpy as np
from typing import Tuple

class FingerprintSegmentation:
    """Fingerprint region detection and segmentation"""
    
    @staticmethod
    def detect_fingerprint_region(image: np.ndarray) -> Tuple[np.ndarray, Tuple]:
        """
        Detect fingerprint region and extract ROI
        
        Args:
            image: Binary image
        
        Returns:
            Tuple of (ROI image, bounding box)
        """
        # Find contours
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return image, (0, 0, image.shape[1], image.shape[0])
        
        # Find largest contour (fingerprint region)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Add padding
        padding = 10
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(image.shape[1] - x, w + 2 * padding)
        h = min(image.shape[0] - y, h + 2 * padding)
        
        # Extract ROI
        roi = image[y:y+h, x:x+w]
        
        return roi, (x, y, w, h)
    
    @staticmethod
    def create_segmentation_mask(image: np.ndarray) -> np.ndarray:
        """
        Create binary mask of fingerprint region
        
        Args:
            image: Input image
        
        Returns:
            Binary mask
        """
        # Threshold
        _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
        
        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        
        # Close small holes
        mask = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Remove small objects
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return mask
```

---

### Task 1.3: Create Ridge Enhancement Module (Days 3-4)

**File**: `backend/app/processing/ridge_enhancement.py`

**Purpose**: Enhance ridge patterns using Gabor filters

```python
import cv2
import numpy as np
from typing import List

class RidgeEnhancement:
    """Ridge pattern enhancement using Gabor filters"""
    
    @staticmethod
    def estimate_ridge_orientation(image: np.ndarray, 
                                   block_size: int = 32) -> np.ndarray:
        """
        Estimate local ridge orientation
        
        Args:
            image: Input image
            block_size: Size of analysis blocks
        
        Returns:
            Orientation field
        """
        # Compute gradients
        gx = cv2.Sobel(image, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(image, cv2.CV_32F, 0, 1, ksize=3)
        
        # Compute orientation
        orientation = np.arctan2(gy, gx)
        
        # Smooth orientation field
        orientation = cv2.blur(orientation, (block_size, block_size))
        
        return orientation
    
    @staticmethod
    def create_gabor_filters(orientations: int = 8,
                            frequencies: int = 5) -> List[np.ndarray]:
        """
        Create bank of Gabor filters
        
        Args:
            orientations: Number of orientation angles
            frequencies: Number of frequency bands
        
        Returns:
            List of Gabor filter kernels
        """
        filters = []
        
        for orientation in range(orientations):
            theta = orientation * np.pi / orientations
            
            for frequency in range(1, frequencies + 1):
                lambda_val = 10.0 / frequency
                gamma = 0.5
                psi = 0
                
                kernel_size = int(2 * np.ceil(3 * lambda_val) + 1)
                if kernel_size % 2 == 0:
                    kernel_size += 1
                
                kernel = cv2.getGaborKernel((kernel_size, kernel_size),
                                           lambda_val, theta, lambda_val,
                                           gamma, psi)
                filters.append(kernel)
        
        return filters
    
    @staticmethod
    def apply_gabor_filters(image: np.ndarray, 
                           filters: List[np.ndarray]) -> np.ndarray:
        """
        Apply Gabor filter bank
        
        Args:
            image: Input image
            filters: List of Gabor filters
        
        Returns:
            Enhanced image
        """
        responses = []
        
        for kernel in filters:
            response = cv2.filter2D(image, cv2.CV_32F, kernel)
            responses.append(response)
        
        # Combine responses
        enhanced = np.mean(responses, axis=0)
        enhanced = cv2.normalize(enhanced, None, 0, 255, cv2.NORM_MINMAX)
        
        return enhanced.astype(np.uint8)
```

---

### Task 1.4: Create Skeletonization Module (Days 4-5)

**File**: `backend/app/processing/skeletonization.py`

**Purpose**: Extract ridge skeleton for feature extraction

```python
import cv2
import numpy as np

class Skeletonization:
    """Ridge skeleton extraction"""
    
    @staticmethod
    def extract_skeleton(image: np.ndarray) -> np.ndarray:
        """
        Extract ridge skeleton using thinning
        
        Args:
            image: Binary image
        
        Returns:
            Skeleton image
        """
        # Ensure binary image
        _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
        
        # Apply thinning
        skeleton = cv2.ximgproc.thinning(binary, 
                                        thinningType=cv2.ximgproc.THINNING_ZHANGSUEN)
        
        # Clean up small artifacts
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        skeleton = cv2.morphologyEx(skeleton, cv2.MORPH_OPEN, kernel)
        
        return skeleton
```

---

### Task 1.5: Create Feature Extractor Module (Days 5-7)

**File**: `backend/app/processing/feature_extractor.py`

**Purpose**: Extract all fingerprint features

```python
import cv2
import numpy as np
from enum import Enum
from typing import Dict, List, Tuple

class PatternType(str, Enum):
    WHORL = "whorl"
    LOOP = "loop"
    ARCH = "arch"
    TENTED_ARCH = "tented_arch"
    COMPOSITE = "composite"

class FingerprintFeatureExtractor:
    """Extract fingerprint features from skeleton"""
    
    @staticmethod
    def detect_pattern_type(image: np.ndarray) -> PatternType:
        """
        Detect fingerprint pattern type
        
        Args:
            image: Skeleton image
        
        Returns:
            Pattern type
        """
        # Find contours
        contours, _ = cv2.findContours(image, cv2.RETR_TREE, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return PatternType.ARCH
        
        # Analyze largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        perimeter = cv2.arcLength(largest_contour, True)
        
        if perimeter == 0:
            return PatternType.ARCH
        
        # Calculate circularity
        circularity = 4 * np.pi * area / (perimeter ** 2)
        
        # Classify based on circularity
        if circularity > 0.7:
            return PatternType.WHORL
        elif circularity > 0.5:
            return PatternType.LOOP
        else:
            return PatternType.ARCH
    
    @staticmethod
    def count_ridges(image: np.ndarray) -> int:
        """
        Estimate ridge count
        
        Args:
            image: Skeleton image
        
        Returns:
            Estimated ridge count
        """
        # Count horizontal ridge crossings
        horizontal_sum = np.sum(image, axis=1)
        crossings = np.sum(np.diff((horizontal_sum > 0).astype(int)) != 0)
        
        return int(crossings / 2)
    
    @staticmethod
    def detect_core_points(image: np.ndarray) -> List[Tuple[int, int]]:
        """
        Detect core points (ridge centers)
        
        Args:
            image: Skeleton image
        
        Returns:
            List of core point coordinates
        """
        # Use corner detection
        corners = cv2.goodFeaturesToTrack(image, maxCorners=10, 
                                         qualityLevel=0.01, minDistance=10)
        
        if corners is None:
            return []
        
        return [(int(x), int(y)) for x, y in corners[:, 0]]
    
    @staticmethod
    def detect_delta_points(image: np.ndarray) -> List[Tuple[int, int]]:
        """
        Detect delta points (ridge bifurcations)
        
        Args:
            image: Skeleton image
        
        Returns:
            List of delta point coordinates
        """
        # Find bifurcation points
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        dilated = cv2.dilate(image, kernel, iterations=1)
        diff = cv2.absdiff(image, dilated)
        
        # Find contours in difference
        contours, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        deltas = []
        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                deltas.append((cx, cy))
        
        return deltas
    
    @staticmethod
    def extract_minutiae(image: np.ndarray) -> Dict:
        """
        Extract minutiae points
        
        Args:
            image: Skeleton image
        
        Returns:
            Minutiae statistics
        """
        # Count ridge endings and bifurcations
        endings = 0
        bifurcations = 0
        
        for i in range(1, image.shape[0] - 1):
            for j in range(1, image.shape[1] - 1):
                if image[i, j] > 0:
                    # Count neighbors
                    neighbors = np.sum(image[i-1:i+2, j-1:j+2] > 0) - 1
                    
                    if neighbors == 1:
                        endings += 1
                    elif neighbors >= 3:
                        bifurcations += 1
        
        return {
            "endings": endings,
            "bifurcations": bifurcations,
            "total": endings + bifurcations
        }
    
    @staticmethod
    def calculate_ridge_density(image: np.ndarray) -> float:
        """
        Calculate ridge density
        
        Args:
            image: Skeleton image
        
        Returns:
            Ridge density (0-1)
        """
        ridge_pixels = np.sum(image > 0)
        total_pixels = image.size
        
        return float(ridge_pixels / total_pixels)
    
    @staticmethod
    def measure_orientation_stability(image: np.ndarray) -> float:
        """
        Measure orientation consistency
        
        Args:
            image: Skeleton image
        
        Returns:
            Stability score (0-1)
        """
        # Compute gradients
        gx = cv2.Sobel(image, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(image, cv2.CV_32F, 0, 1, ksize=3)
        
        # Compute orientation
        orientation = np.arctan2(gy, gx)
        
        # Measure variance (lower = more stable)
        if np.std(orientation) == 0:
            return 1.0
        
        stability = 1.0 - (np.std(orientation) / np.pi)
        
        return float(np.clip(stability, 0, 1))
    
    @staticmethod
    def extract_all_features(image: np.ndarray) -> Dict:
        """
        Extract all fingerprint features
        
        Args:
            image: Skeleton image
        
        Returns:
            Dictionary of all features
        """
        core_points = FingerprintFeatureExtractor.detect_core_points(image)
        delta_points = FingerprintFeatureExtractor.detect_delta_points(image)
        minutiae = FingerprintFeatureExtractor.extract_minutiae(image)
        
        return {
            "pattern_type": FingerprintFeatureExtractor.detect_pattern_type(image).value,
            "ridge_count": FingerprintFeatureExtractor.count_ridges(image),
            "core_count": len(core_points),
            "delta_count": len(delta_points),
            "minutiae_endings": minutiae["endings"],
            "minutiae_bifurcations": minutiae["bifurcations"],
            "minutiae_total": minutiae["total"],
            "ridge_density": FingerprintFeatureExtractor.calculate_ridge_density(image),
            "orientation_stability": FingerprintFeatureExtractor.measure_orientation_stability(image)
        }
```

---

### Task 1.6: Update Main Image Processor (Days 7-8)

**File**: `backend/app/processing/image_processor.py` (UPDATE)

```python
import cv2
import numpy as np
from .preprocessing import FingerprintPreprocessor
from .segmentation import FingerprintSegmentation
from .ridge_enhancement import RidgeEnhancement
from .skeletonization import Skeletonization
from .feature_extractor import FingerprintFeatureExtractor

class ImageProcessingService:
    
    @staticmethod
    def process_fingerprint(image_data: bytes) -> dict:
        """
        Complete fingerprint processing pipeline
        
        Args:
            image_data: Raw image bytes
        
        Returns:
            Processing results with features
        """
        try:
            # Decode image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            
            if image is None:
                return {"error": "Failed to decode image", "success": False}
            
            # 1. Preprocessing
            preprocessed = FingerprintPreprocessor.preprocess_fingerprint(image)
            
            # 2. Segmentation
            segmented, roi = FingerprintSegmentation.detect_fingerprint_region(preprocessed)
            
            # 3. Ridge Enhancement
            filters = RidgeEnhancement.create_gabor_filters()
            enhanced = RidgeEnhancement.apply_gabor_filters(segmented, filters)
            
            # 4. Skeletonization
            skeleton = Skeletonization.extract_skeleton(enhanced)
            
            # 5. Feature Extraction
            features = FingerprintFeatureExtractor.extract_all_features(skeleton)
            
            # 6. Quality Score
            quality_score = ImageProcessingService.calculate_quality_score(image)
            
            return {
                "success": True,
                "quality_score": quality_score,
                "features": features
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def calculate_quality_score(image: np.ndarray) -> float:
        """Calculate image quality score"""
        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        quality_score = min(100.0, (laplacian_var / 500.0) * 100)
        return float(max(0.0, quality_score))
```

---

## Testing Checklist

- [ ] All preprocessing functions tested
- [ ] Segmentation correctly identifies fingerprint region
- [ ] Ridge enhancement produces clear patterns
- [ ] Skeletonization extracts ridge skeleton
- [ ] Feature extraction returns all required features
- [ ] Complete pipeline processes image in < 5 seconds
- [ ] All unit tests passing
- [ ] Integration tests passing

---

## Deliverables

### Code Files
- [x] `backend/app/processing/preprocessing.py`
- [x] `backend/app/processing/segmentation.py`
- [x] `backend/app/processing/ridge_enhancement.py`
- [x] `backend/app/processing/skeletonization.py`
- [x] `backend/app/processing/feature_extractor.py`
- [x] Updated `backend/app/processing/image_processor.py`

### Tests
- [ ] `backend/tests/test_preprocessing.py`
- [ ] `backend/tests/test_segmentation.py`
- [ ] `backend/tests/test_ridge_enhancement.py`
- [ ] `backend/tests/test_skeletonization.py`
- [ ] `backend/tests/test_feature_extraction.py`

### Documentation
- [ ] Image processing pipeline documentation
- [ ] Feature extraction guide
- [ ] API documentation updates

---

## Success Criteria

✅ All preprocessing functions working  
✅ Ridge enhancement producing clear patterns  
✅ Skeletonization extracting ridge skeleton  
✅ Feature extraction returning all required features  
✅ All unit tests passing  
✅ Processing time < 5 seconds per image  
✅ Quality score accurately reflecting image quality  

---

**Sprint 1 Implementation Guide Created**: May 19, 2026  
**Ready to Execute**: Yes
