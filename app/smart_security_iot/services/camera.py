from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from typing import Union

import cv2


@dataclass(frozen=True)
class CameraOpenResult:
    cap: cv2.VideoCapture | None
    backend: str
    error: str | None


def _is_windows() -> bool:
    return sys.platform.startswith("win")


def open_camera(source: Union[int, str]) -> CameraOpenResult:
    """
    OpenCV on Windows sometimes fails with MSMF backend. We try a safe sequence:
    - For local webcam indexes: prefer DirectShow (CAP_DSHOW) then default
    - For RTSP/URLs: prefer FFmpeg (CAP_FFMPEG) then default
    """
    tried: list[str] = []

    def _try_open(cap: cv2.VideoCapture, backend_name: str) -> CameraOpenResult:
        if cap.isOpened():
            return CameraOpenResult(cap=cap, backend=backend_name, error=None)
        cap.release()
        return CameraOpenResult(cap=None, backend=backend_name, error="open failed")

    if isinstance(source, int):
        if _is_windows():
            tried.append("DSHOW")
            r = _try_open(cv2.VideoCapture(source, cv2.CAP_DSHOW), "DSHOW")
            if r.cap is not None:
                return r
        tried.append("DEFAULT")
        r = _try_open(cv2.VideoCapture(source), "DEFAULT")
        if r.cap is not None:
            return r
        return CameraOpenResult(cap=None, backend=",".join(tried), error="unable to open webcam")

    # string source
    if _is_windows():
        # If source is a digit string, treat it as webcam index.
        if str(source).isdigit():
            return open_camera(int(source))

    tried.append("FFMPEG")
    r = _try_open(cv2.VideoCapture(source, cv2.CAP_FFMPEG), "FFMPEG")
    if r.cap is not None:
        return r

    tried.append("DEFAULT")
    r = _try_open(cv2.VideoCapture(source), "DEFAULT")
    if r.cap is not None:
        return r

    return CameraOpenResult(cap=None, backend=",".join(tried), error="unable to open camera source")


def safe_read(cap: cv2.VideoCapture, *, max_retries: int = 1, retry_sleep_s: float = 0.0):
    """
    Some backends return intermittent read failures; retry a few times.
    Returns (ok, frame).
    """
    for _ in range(max_retries):
        ok, frame = cap.read()
        if ok and frame is not None:
            return True, frame
        if retry_sleep_s > 0:
            time.sleep(retry_sleep_s)
    return False, None
