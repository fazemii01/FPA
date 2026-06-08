"""Ridge skeletonization (thinning to 1-pixel-wide skeleton).

Uses cv2.ximgproc.thinning when available; falls back to a pure-numpy
Zhang-Suen implementation so the module works without opencv-contrib.
"""
from __future__ import annotations

import cv2
import numpy as np


class Skeletonization:
    def extract_skeleton(self, binary: np.ndarray) -> np.ndarray:
        """Input: 0/255 uint8 image with ridges = 255. Output: 0/255 skeleton."""
        if binary.dtype != np.uint8:
            binary = binary.astype(np.uint8)
        if binary.max() == 0:
            return binary.copy()
        ximgproc = getattr(cv2, "ximgproc", None)
        if ximgproc is not None and hasattr(ximgproc, "thinning"):
            try:
                return ximgproc.thinning(binary, thinningType=ximgproc.THINNING_ZHANGSUEN)
            except cv2.error:
                pass
        return _zhang_suen(binary)


def _zhang_suen(image: np.ndarray) -> np.ndarray:
    """Pure-numpy Zhang-Suen thinning. Slower but dependency-free."""
    img = (image > 0).astype(np.uint8)
    prev = np.zeros_like(img)
    iterations = 0
    while not np.array_equal(img, prev) and iterations < 100:
        prev = img.copy()
        for step in (0, 1):
            marker = np.zeros_like(img)
            P = [img[1:-1, 1:-1]]
            P.append(img[0:-2, 1:-1])  # P2
            P.append(img[0:-2, 2:])    # P3
            P.append(img[1:-1, 2:])    # P4
            P.append(img[2:, 2:])      # P5
            P.append(img[2:, 1:-1])    # P6
            P.append(img[2:, 0:-2])    # P7
            P.append(img[1:-1, 0:-2])  # P8
            P.append(img[0:-2, 0:-2])  # P9
            B = sum(P[i] for i in range(1, 9))
            # transitions 0->1 in ordered sequence P2..P9..P2
            seq = [P[i] for i in [2, 3, 4, 5, 6, 7, 8, 1, 2]]
            A = np.zeros_like(P[1])
            for k in range(8):
                A += ((seq[k] == 0) & (seq[k + 1] == 1)).astype(np.uint8)
            if step == 0:
                cond = (P[0] == 1) & (B >= 2) & (B <= 6) & (A == 1) \
                    & (P[1] * P[3] * P[5] == 0) & (P[3] * P[5] * P[7] == 0)
            else:
                cond = (P[0] == 1) & (B >= 2) & (B <= 6) & (A == 1) \
                    & (P[1] * P[3] * P[7] == 0) & (P[1] * P[5] * P[7] == 0)
            marker[1:-1, 1:-1] = cond.astype(np.uint8)
            img = img & (1 - marker)
        iterations += 1
    return (img * 255).astype(np.uint8)
