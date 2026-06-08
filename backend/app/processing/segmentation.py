"""Fingerprint segmentation: separate ridge area from background.

Uses block-wise variance thresholding which is robust to lighting.
"""
from __future__ import annotations

import cv2
import numpy as np


class FingerprintSegmentation:
    def __init__(self, block_size: int = 16, variance_threshold: float = 100.0) -> None:
        self.block_size = block_size
        self.variance_threshold = variance_threshold

    def create_segmentation_mask(self, gray: np.ndarray) -> np.ndarray:
        """Return a uint8 mask (0/255) where 255 marks fingerprint area."""
        h, w = gray.shape
        bs = self.block_size
        mask = np.zeros((h, w), dtype=np.uint8)
        img = gray.astype(np.float32)
        for y in range(0, h, bs):
            for x in range(0, w, bs):
                block = img[y : y + bs, x : x + bs]
                if block.size == 0:
                    continue
                if float(block.var()) >= self.variance_threshold:
                    mask[y : y + bs, x : x + bs] = 255
        # smooth boundary
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        return mask

    def detect_fingerprint_region(self, gray: np.ndarray) -> tuple[int, int, int, int]:
        """Return bounding box (x, y, w, h) of the foreground area; (0,0,0,0) if none."""
        mask = self.create_segmentation_mask(gray)
        ys, xs = np.where(mask > 0)
        if xs.size == 0:
            return (0, 0, 0, 0)
        x0, x1 = int(xs.min()), int(xs.max())
        y0, y1 = int(ys.min()), int(ys.max())
        return (x0, y0, x1 - x0 + 1, y1 - y0 + 1)
