from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(frozen=True)
class LbphKnown:
    user_id: int
    label: str
    image_path: str


class LbphEngine:
    """
    Practical fallback for Windows without dlib:
    - Face detection via Haar cascade
    - Recognition via LBPH (cv2.face.*) from opencv-contrib-python
    """

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        if not hasattr(cv2, "face"):
            raise RuntimeError("cv2.face not available (install opencv-contrib-python)")
        self._recognizer = cv2.face.LBPHFaceRecognizer_create()
        self._detector = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"))
        self._trained = False
        self._label_map: dict[int, tuple[int, str]] = {}

    def train_from_photos(self, known: list[LbphKnown]) -> None:
        images: list[np.ndarray] = []
        labels: list[int] = []
        self._label_map.clear()

        idx = 0
        for k in known:
            p = Path(k.image_path)
            if not p.exists():
                continue
            img = cv2.imread(str(p))
            if img is None:
                continue
            face = self._extract_face(img)
            if face is None:
                continue
            images.append(face)
            labels.append(idx)
            self._label_map[idx] = (k.user_id, k.label)
            idx += 1

        if not images:
            self._trained = False
            self._logger.warning("LBPH: no training images available")
            return

        self._recognizer.train(images, np.asarray(labels, dtype=np.int32))
        self._trained = True
        self._logger.info("LBPH: trained with %d identities", len(images))

    def predict(self, bgr_frame: np.ndarray) -> tuple[int | None, str, float]:
        if not self._trained:
            return None, "UNKNOWN", 0.0
        face = self._extract_face(bgr_frame)
        if face is None:
            return None, "UNKNOWN", 0.0

        label_idx, dist = self._recognizer.predict(face)
        if label_idx not in self._label_map:
            return None, "UNKNOWN", 0.0

        user_id, label = self._label_map[label_idx]
        # Convert LBPH distance into a conservative confidence. Lower distance -> higher confidence.
        # Typical LBPH distances vary a lot; we clamp into [0..1] with a strict curve.
        confidence = float(max(0.0, min(1.0, 1.0 - (dist / 80.0))))
        return user_id, label, confidence

    def _extract_face(self, bgr: np.ndarray) -> np.ndarray | None:
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        faces = self._detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
        if len(faces) == 0:
            return None
        x, y, w, h = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)[0]
        roi = gray[y : y + h, x : x + w]
        roi = cv2.resize(roi, (200, 200), interpolation=cv2.INTER_CUBIC)
        return roi
