from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import cv2


@dataclass(frozen=True)
class FaceMatch:
    user_id: int | None
    label: str
    confidence: float
    box: tuple[int, int, int, int] | None = None  # left, top, right, bottom


class FaceEngine:
    """
    Lightweight face pipeline:
    - Primary: face_recognition encodings (if available)
    - Fallback: OpenCV LBPH (opencv-contrib-python) based on stored user photos
    """

    def __init__(self, logger: logging.Logger, threshold: float) -> None:
        self._logger = logger
        self._threshold = threshold
        self._fr = None
        self._lbph = None
        self._haar = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"))
        try:
            import face_recognition  # type: ignore

            self._fr = face_recognition
            self._logger.info("face_recognition enabled (primary engine)")
        except Exception as ex:  # pragma: no cover
            self._logger.info("face_recognition not available; falling back to LBPH: %s", ex)
            self._try_enable_lbph()

    def _try_enable_lbph(self) -> None:
        try:
            if not hasattr(cv2, "face"):
                self._logger.warning("OpenCV contrib (cv2.face) not available; LBPH disabled")
                return
            self._lbph = cv2
            self._logger.info("LBPH fallback enabled (opencv-contrib-python)")
        except Exception as ex:  # pragma: no cover
            self._logger.warning("LBPH fallback not available: %s", ex)

    @property
    def is_available(self) -> bool:
        return self._fr is not None or self._lbph is not None

    @property
    def has_face_recognition(self) -> bool:
        return self._fr is not None

    def extract_encoding(self, rgb_frame: np.ndarray) -> Optional[np.ndarray]:
        if self._fr is None:
            return None
        try:
            img = self._sanitize_rgb8(rgb_frame)
            locations = self._try_face_locations(img)
            if not locations:
                enhanced = self._enhance_for_detection(img)
                locations = self._try_face_locations(enhanced)
                img = enhanced
            if not locations:
                # Fallback to OpenCV Haar cascade for the first face box.
                haar_boxes = self._haar_boxes_rgb(img)
                if not haar_boxes:
                    return None
                left, top, right, bottom = haar_boxes[0]
                locations = [(top, right, bottom, left)]

            encodings = self._fr.face_encodings(img, known_face_locations=locations)
            if not encodings:
                return None
            return np.asarray(encodings[0], dtype=np.float32)
        except Exception as ex:
            # Keep this quiet by default; UI will show a friendly message.
            self._logger.debug("face_recognition extract failed: %s", ex)
            return None

    def _try_face_locations(self, img: np.ndarray):
        # Progressive upsample improves detection at the cost of CPU.
        for ups in (0, 1, 2):
            locs = self._fr.face_locations(img, number_of_times_to_upsample=ups, model="hog")
            if locs:
                return locs
        return []

    @staticmethod
    def _enhance_for_detection(rgb8: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(rgb8, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l2 = clahe.apply(l)
        lab2 = cv2.merge((l2, a, b))
        out = cv2.cvtColor(lab2, cv2.COLOR_LAB2RGB)
        return np.ascontiguousarray(out, dtype=np.uint8)

    @staticmethod
    def _sanitize_rgb8(img: np.ndarray) -> np.ndarray:
        """
        face_recognition/dlib expects:
        - uint8 RGB (H,W,3) or uint8 gray (H,W)
        Some camera backends can produce non-uint8 frames; normalize conservatively.
        """
        if img is None:
            raise ValueError("img is None")

        arr = np.asarray(img)

        # Convert to uint8 if needed.
        if arr.dtype != np.uint8:
            # If values look like 0..1 floats, scale up; otherwise clip.
            amax = float(np.nanmax(arr)) if arr.size else 0.0
            amin = float(np.nanmin(arr)) if arr.size else 0.0
            if amax <= 1.0 and amin >= 0.0:
                arr = (arr * 255.0).astype(np.uint8)
            else:
                arr = np.clip(arr, 0, 255).astype(np.uint8)

        # Handle channel shapes: RGB, RGBA, Gray
        if arr.ndim == 2:
            # Gray is acceptable, but we keep as-is.
            pass
        elif arr.ndim == 3:
            if arr.shape[2] == 4:
                arr = arr[:, :, :3]
            elif arr.shape[2] != 3:
                raise ValueError(f"unsupported channel count: {arr.shape[2]}")
        else:
            raise ValueError(f"unsupported image ndim: {arr.ndim}")

        # Ensure strict uint8 contiguous memory for dlib.
        arr = np.ascontiguousarray(arr, dtype=np.uint8)
        return arr

    def match_encoding(self, encoding: np.ndarray, known: list[tuple[int, str, np.ndarray]]) -> FaceMatch:
        if not known:
            return FaceMatch(user_id=None, label="UNKNOWN", confidence=0.0)
        # Use face_recognition distance if possible, else fallback to L2
        distances = []
        for user_id, label, ref in known:
            d = float(np.linalg.norm(ref - encoding))
            distances.append((d, user_id, label))
        distances.sort(key=lambda x: x[0])
        best_d, best_id, best_label = distances[0]

        confidence = max(0.0, min(1.0, 1.0 - best_d))
        if best_d <= self._threshold:
            return FaceMatch(user_id=best_id, label=best_label, confidence=confidence)
        return FaceMatch(user_id=None, label="UNKNOWN", confidence=confidence)

    def can_enroll(self) -> bool:
        return self._fr is not None or self._lbph is not None

    def identify_all(self, rgb_frame: np.ndarray, known: list[tuple[int, str, np.ndarray]]) -> list[FaceMatch]:
        """
        Detect and identify all faces in a frame (face_recognition only).
        Returns a list with bounding boxes.
        """
        if self._fr is None:
            return []
        img = self._sanitize_rgb8(rgb_frame)
        try:
            locations = self._try_face_locations(img)
            if not locations:
                enhanced = self._enhance_for_detection(img)
                locations = self._try_face_locations(enhanced)
                img = enhanced
            if not locations:
                return []

            encodings = self._fr.face_encodings(img, known_face_locations=locations)
            out: list[FaceMatch] = []
            for loc, enc in zip(locations, encodings, strict=False):
                # loc is (top, right, bottom, left)
                top, right, bottom, left = loc
                if known:
                    m = self.match_encoding(np.asarray(enc, dtype=np.float32), known)
                    out.append(
                        FaceMatch(
                            user_id=m.user_id,
                            label=m.label,
                            confidence=m.confidence,
                            box=(left, top, right, bottom),
                        )
                    )
                else:
                    out.append(FaceMatch(user_id=None, label="UNKNOWN", confidence=0.0, box=(left, top, right, bottom)))
            return out
        except Exception as ex:
            self._logger.debug("face_recognition identify_all failed: %s", ex)
            return []

    def detect_boxes(self, rgb_frame: np.ndarray) -> list[tuple[int, int, int, int]]:
        """
        Detect face boxes only. Returns (left, top, right, bottom).
        """
        if self._fr is None:
            return []
        img = self._sanitize_rgb8(rgb_frame)
        try:
            locations = self._try_face_locations(img)
            if not locations:
                enhanced = self._enhance_for_detection(img)
                locations = self._try_face_locations(enhanced)
                img = enhanced
            out: list[tuple[int, int, int, int]] = []
            for top, right, bottom, left in locations:
                out.append((left, top, right, bottom))
            if out:
                return out
            # Haar fallback
            return self._haar_boxes_rgb(img)
        except Exception as ex:
            self._logger.debug("face_recognition detect_boxes failed: %s", ex)
            return self._haar_boxes_rgb(img)

    def _haar_boxes_rgb(self, rgb8: np.ndarray) -> list[tuple[int, int, int, int]]:
        try:
            gray = cv2.cvtColor(rgb8, cv2.COLOR_RGB2GRAY)
            faces = self._haar.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
            if len(faces) == 0:
                return []
            # Sort by area, return (l,t,r,b)
            faces_sorted = sorted(faces, key=lambda r: int(r[2]) * int(r[3]), reverse=True)
            out: list[tuple[int, int, int, int]] = []
            for x, y, w, h in faces_sorted:
                out.append((int(x), int(y), int(x + w), int(y + h)))
            return out
        except Exception:
            return []
