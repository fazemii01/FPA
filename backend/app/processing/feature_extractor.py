"""Extract dermatoglyphic features required by PRD FR-07 and FR-08.

Features computed:
- pattern_type: WHORL / LOOP / ARCH / TENTED_ARCH / COMPOSITE
- ridge_count: estimated ridges along the principal axis
- core_points / delta_points: singular points from orientation field
- minutiae: endpoints and bifurcations from the skeleton
- ridge_density: ridges per unit area
- orientation_stability: variance of orientation across blocks (0..1, higher = stabler)
"""
from __future__ import annotations

import cv2
import numpy as np
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple

from .preprocessing import FingerprintPreprocessor
from .segmentation import FingerprintSegmentation
from .ridge_enhancement import RidgeEnhancement
from .skeletonization import Skeletonization


class PatternType(str, Enum):
    WHORL = "whorl"
    LOOP = "loop"
    ARCH = "arch"
    TENTED_ARCH = "tented_arch"
    COMPOSITE = "composite"
    UNKNOWN = "unknown"


@dataclass
class Minutia:
    x: int
    y: int
    kind: str  # "endpoint" | "bifurcation"


@dataclass
class FingerprintFeatures:
    pattern_type: PatternType = PatternType.UNKNOWN
    ridge_count: int = 0
    core_points: List[Tuple[int, int]] = field(default_factory=list)
    delta_points: List[Tuple[int, int]] = field(default_factory=list)
    minutiae: List[Minutia] = field(default_factory=list)
    ridge_density: float = 0.0
    orientation_stability: float = 0.0
    quality_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "pattern_type": self.pattern_type.value,
            "ridge_count": int(self.ridge_count),
            "core_points": [[int(x), int(y)] for x, y in self.core_points],
            "delta_points": [[int(x), int(y)] for x, y in self.delta_points],
            "minutiae": [
                {"x": int(m.x), "y": int(m.y), "kind": m.kind} for m in self.minutiae
            ],
            "ridge_density": float(self.ridge_density),
            "orientation_stability": float(self.orientation_stability),
            "quality_score": float(self.quality_score),
        }


class FingerprintFeatureExtractor:
    def __init__(self) -> None:
        self.preprocessor = FingerprintPreprocessor()
        self.segmentation = FingerprintSegmentation()
        self.ridge = RidgeEnhancement()
        self.skeleton = Skeletonization()

    # ---------- public ----------

    def extract_all_features(self, image: np.ndarray) -> FingerprintFeatures:
        steps = self.preprocessor.preprocess_fingerprint(image)
        mask = self.segmentation.create_segmentation_mask(steps["enhanced"])

        orient = self.ridge.estimate_ridge_orientation(steps["enhanced"])
        gabor = self.ridge.apply_gabor_filters(steps["enhanced"])
        # Binarize the Gabor response then mask to fingerprint area
        _, gabor_bin = cv2.threshold(gabor, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        gabor_bin = cv2.bitwise_and(gabor_bin, mask)

        skel = self.skeleton.extract_skeleton(gabor_bin)

        cores = self.detect_core_points(orient, mask)
        deltas = self.detect_delta_points(orient, mask)
        minutiae = self.extract_minutiae(skel, mask)
        ridge_count = self.count_ridges(skel)
        density = self.calculate_ridge_density(skel, mask)
        stability = self.measure_orientation_stability(orient, mask)
        pattern = self.detect_pattern_type(cores, deltas, stability)
        quality = self._quality_from_features(stability, density, ridge_count)

        return FingerprintFeatures(
            pattern_type=pattern,
            ridge_count=ridge_count,
            core_points=cores,
            delta_points=deltas,
            minutiae=minutiae,
            ridge_density=density,
            orientation_stability=stability,
            quality_score=quality,
        )

    # ---------- helpers ----------

    @staticmethod
    def count_ridges(skeleton: np.ndarray) -> int:
        """Count ridges by intersecting a horizontal scan line at mid-height."""
        if skeleton.size == 0:
            return 0
        mid = skeleton.shape[0] // 2
        line = skeleton[mid] > 0
        transitions = int(np.sum((line[1:].astype(int) - line[:-1].astype(int)) == 1))
        # also try a few rows around mid and take the median for robustness
        rows = []
        for offset in (-8, -4, 0, 4, 8):
            r = mid + offset
            if 0 <= r < skeleton.shape[0]:
                line = skeleton[r] > 0
                rows.append(int(np.sum((line[1:].astype(int) - line[:-1].astype(int)) == 1)))
        if rows:
            transitions = int(np.median(rows))
        return transitions

    @staticmethod
    def detect_core_points(
        orientation: np.ndarray, mask: np.ndarray, block: int = 16
    ) -> List[Tuple[int, int]]:
        """Find singular points using the Poincaré index ≈ +π (cores)."""
        return _poincare_singular_points(orientation, mask, block, target=+np.pi)

    @staticmethod
    def detect_delta_points(
        orientation: np.ndarray, mask: np.ndarray, block: int = 16
    ) -> List[Tuple[int, int]]:
        """Singular points with Poincaré index ≈ -π (deltas)."""
        return _poincare_singular_points(orientation, mask, block, target=-np.pi)

    @staticmethod
    def extract_minutiae(skeleton: np.ndarray, mask: np.ndarray) -> List[Minutia]:
        """Endpoints (1 neighbour) and bifurcations (3 neighbours) on the skeleton."""
        if skeleton.size == 0:
            return []
        bin_skel = (skeleton > 0).astype(np.uint8)
        kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.uint8)
        neighbours = cv2.filter2D(bin_skel, ddepth=cv2.CV_16S, kernel=kernel)
        h, w = bin_skel.shape
        out: List[Minutia] = []
        # Restrict to interior of mask to reduce border noise
        if mask is not None and mask.shape == bin_skel.shape:
            interior = cv2.erode(mask, np.ones((9, 9), np.uint8))
        else:
            interior = np.full_like(bin_skel, 255)
        ys, xs = np.where((bin_skel == 1) & (interior > 0))
        for y, x in zip(ys, xs):
            if 0 < y < h - 1 and 0 < x < w - 1:
                n = int(neighbours[y, x])
                if n == 1:
                    out.append(Minutia(x=int(x), y=int(y), kind="endpoint"))
                elif n == 3:
                    out.append(Minutia(x=int(x), y=int(y), kind="bifurcation"))
        return out

    @staticmethod
    def calculate_ridge_density(skeleton: np.ndarray, mask: np.ndarray) -> float:
        """Skeleton-pixels per fingerprint-area-pixel."""
        if skeleton.size == 0:
            return 0.0
        area = int(np.count_nonzero(mask)) if mask is not None else int(skeleton.size)
        if area == 0:
            return 0.0
        return float(np.count_nonzero(skeleton)) / float(area)

    @staticmethod
    def measure_orientation_stability(orientation: np.ndarray, mask: np.ndarray) -> float:
        """1 - normalized circular variance of orientations. Higher = more stable."""
        if orientation.size == 0:
            return 0.0
        if mask is not None:
            theta = orientation[mask > 0]
        else:
            theta = orientation.ravel()
        if theta.size == 0:
            return 0.0
        # Orientations are in [0, π). Double-angle to get a proper circular variance.
        c = float(np.cos(2 * theta).mean())
        s = float(np.sin(2 * theta).mean())
        r = float(np.sqrt(c * c + s * s))  # 0..1
        return float(max(0.0, min(1.0, r)))

    @staticmethod
    def detect_pattern_type(
        cores: List[Tuple[int, int]],
        deltas: List[Tuple[int, int]],
        stability: float,
    ) -> PatternType:
        n_core, n_delta = len(cores), len(deltas)
        
        # Whorls typically have high curvature and multiple singular point clusters
        if n_core >= 8 and n_delta >= 6:
            return PatternType.WHORL
            
        # Loops have intermediate curvature and singular point counts
        if (n_core >= 2 and n_delta >= 2) or (n_core >= 2 and n_delta >= 1) or (n_core >= 1 and n_delta >= 2):
            return PatternType.LOOP
            
        # Arches/Tented Arches have very low counts of singular points
        if n_core == 1:
            return PatternType.TENTED_ARCH
            
        if n_core == 0:
            return PatternType.ARCH
            
        return PatternType.COMPOSITE

    @staticmethod
    def _quality_from_features(stability: float, density: float, ridge_count: int) -> float:
        """0..100 quality score combining the three signals."""
        s = max(0.0, min(1.0, stability))
        # density healthy range ~0.05..0.20
        d_norm = max(0.0, min(1.0, density / 0.15))
        r_norm = max(0.0, min(1.0, ridge_count / 25.0))
        return float(round(100.0 * (0.5 * s + 0.3 * d_norm + 0.2 * r_norm), 2))


# ---------- internals ----------

def _poincare_singular_points(
    orientation: np.ndarray,
    mask: np.ndarray,
    block: int,
    target: float,
    tolerance: float = 0.5,
) -> List[Tuple[int, int]]:
    """Locate singular points by summing orientation changes around a small loop."""
    h, w = orientation.shape
    pts: List[Tuple[int, int]] = []
    
    # Erode the mask to avoid border/background noise
    if mask is not None:
        kernel = np.ones((25, 25), np.uint8)
        eroded_mask = cv2.erode(mask, kernel)
    else:
        eroded_mask = None

    radius = 3  # Keep loop radius fixed at 3 to trace local ridge flow
    # 8-neighbour ring offsets (clockwise)
    ring = [
        (-radius, -radius), (-radius, 0), (-radius, radius),
        (0, radius), (radius, radius), (radius, 0),
        (radius, -radius), (0, -radius),
    ]
    # Scan step size must be small (2 pixels) to avoid skipping singular points
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
    return _non_max_suppress(pts, radius=int(block * 2.5))


def _non_max_suppress(points: List[Tuple[int, int]], radius: int) -> List[Tuple[int, int]]:
    if not points:
        return []
    kept: List[Tuple[int, int]] = []
    for x, y in points:
        ok = True
        for kx, ky in kept:
            if (x - kx) ** 2 + (y - ky) ** 2 < radius * radius:
                ok = False
                break
        if ok:
            kept.append((x, y))
    return kept
