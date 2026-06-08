"""Ridge orientation estimation and Gabor enhancement."""
from __future__ import annotations

import cv2
import numpy as np


class RidgeEnhancement:
    def __init__(
        self,
        block_size: int = 16,
        gabor_ksize: int = 21,
        gabor_sigma: float = 4.0,
        gabor_lambda: float = 10.0,
        gabor_gamma: float = 0.5,
        gabor_psi: float = 0.0,
        n_orientations: int = 8,
    ) -> None:
        self.block_size = block_size
        self.gabor_ksize = gabor_ksize
        self.gabor_sigma = gabor_sigma
        self.gabor_lambda = gabor_lambda
        self.gabor_gamma = gabor_gamma
        self.gabor_psi = gabor_psi
        self.n_orientations = n_orientations

    def estimate_ridge_orientation(self, gray: np.ndarray) -> np.ndarray:
        """Block-wise ridge orientation in radians [0, pi). Shape == gray.shape."""
        img = gray.astype(np.float32)
        gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)

        h, w = gray.shape
        bs = self.block_size
        
        # Compute local gradient components vx and vy per pixel
        vx = 2.0 * gx * gy
        vy = gx * gx - gy * gy
        
        # Smooth vx and vy with a Gaussian filter to eliminate local noise
        vx_smooth = cv2.GaussianBlur(vx, (15, 15), 0)
        vy_smooth = cv2.GaussianBlur(vy, (15, 15), 0)

        orient = np.zeros((h, w), dtype=np.float32)
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

    def create_gabor_filters(self) -> list[tuple[float, np.ndarray]]:
        filters: list[tuple[float, np.ndarray]] = []
        for i in range(self.n_orientations):
            theta = i * np.pi / self.n_orientations
            kern = cv2.getGaborKernel(
                ksize=(self.gabor_ksize, self.gabor_ksize),
                sigma=self.gabor_sigma,
                theta=theta,
                lambd=self.gabor_lambda,
                gamma=self.gabor_gamma,
                psi=self.gabor_psi,
                ktype=cv2.CV_32F,
            )
            filters.append((theta, kern))
        return filters

    def apply_gabor_filters(self, gray: np.ndarray) -> np.ndarray:
        """Pick max response across orientations (simple per-pixel enhancement)."""
        gray_f = gray.astype(np.float32)
        accum = np.zeros_like(gray_f)
        for _theta, kern in self.create_gabor_filters():
            resp = cv2.filter2D(gray_f, cv2.CV_32F, kern)
            np.maximum(accum, resp, out=accum)
        accum = cv2.normalize(accum, None, 0, 255, cv2.NORM_MINMAX)
        return accum.astype(np.uint8)
