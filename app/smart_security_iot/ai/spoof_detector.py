from __future__ import annotations

import cv2
import numpy as np


def detect_spoof(rgb_frame: np.ndarray) -> tuple[bool, float, str]:
    gray = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)

    lap = cv2.Laplacian(gray, cv2.CV_64F)
    sharpness = float(np.var(lap))
    sharp_score = min(1.0, sharpness / 300.0)

    lab = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2LAB)
    l = lab[:, :, 0]
    luma_var = float(np.var(l))
    luma_score = min(1.0, luma_var / 800.0)

    f = np.fft.fft2(cv2.resize(gray, (320, 240)))
    fshift = np.fft.fftshift(f)
    magnitude = np.log(np.abs(fshift) + 1)
    h, w = magnitude.shape
    low = magnitude[h//2-10:h//2+10, w//2-10:w//2+10]
    high = magnitude[5:-5, 5:-5]
    ratio = float(np.mean(low)) / max(float(np.mean(high)), 1e-6)
    freq_score = max(0.0, min(1.0, 1.0 - ratio / 2.0))

    overall = float(np.mean([sharp_score, luma_score, freq_score]))
    is_spoof = overall < 0.18

    reasons = []
    if sharp_score < 0.2:
        reasons.append("blurry")
    if luma_score < 0.2:
        reasons.append("flat")
    if freq_score < 0.2:
        reasons.append("no_detail")

    reason = ", ".join(reasons) if reasons else ("spoof" if is_spoof else "real")
    return is_spoof, overall, reason
