from __future__ import annotations

import logging
from pathlib import Path

import numpy as np


class DeepFaceValidator:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._available = False
        self._model = None
        self._checked = False

    def _try_init(self) -> None:
        if self._checked:
            return
        self._checked = True
        try:
            import deepface  # type: ignore
            self._model = deepface
            self._available = True
            self._logger.info("DeepFace enabled (secondary validation)")
        except Exception as ex:
            self._logger.info("DeepFace not available: %s", ex)

    @property
    def is_available(self) -> bool:
        self._try_init()
        return self._available

    def verify(self, face_img: np.ndarray, known_path: str, model_name: str = "Facenet") -> tuple[bool, float]:
        self._try_init()
        if not self._available:
            return True, 1.0
        if not Path(known_path).exists():
            return True, 0.5
        try:
            import deepface  # type: ignore
            result = deepface.DeepFace.verify(
                img1_path=face_img,
                img2_path=known_path,
                model_name=model_name,
                enforce_detection=False,
                silent=True,
            )
            verified = bool(result.get("verified", False))
            distance = float(result.get("distance", 1.0))
            confidence = max(0.0, 1.0 - distance)
            return verified, confidence
        except Exception as ex:
            self._logger.debug("DeepFace verify failed: %s", ex)
            return True, 0.5
