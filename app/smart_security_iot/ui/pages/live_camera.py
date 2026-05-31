from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from smart_security_iot.ai.deepface_validator import DeepFaceValidator
from smart_security_iot.ai.face_engine import FaceEngine
from smart_security_iot.ai.lbph_engine import LbphEngine, LbphKnown
from smart_security_iot.ai.spoof_detector import detect_spoof
from smart_security_iot.core.config import AppConfig
from smart_security_iot.database.db import Database
from smart_security_iot.services.alert_service import AlertService
from smart_security_iot.services.camera import open_camera, safe_read
from smart_security_iot.services.detections import DetectionEvent, DetectionStore
from smart_security_iot.services.plc_service import PlcService
from smart_security_iot.services.users import UserStore


class LiveCameraPage(QWidget):
    def __init__(self, config: AppConfig, db: Database, logger: logging.Logger,
                 plc: PlcService | None = None, alerts: AlertService | None = None) -> None:
        super().__init__()
        self._config = config
        self._db = db
        self._logger = logger
        self._plc = plc
        self._alerts = alerts

        self._cap: cv2.VideoCapture | None = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._rec_timer = QTimer(self)
        self._rec_timer.timeout.connect(self._tick_recognition)
        self._frame_idx = 0
        self._stall_count = 0
        self._display_frame: np.ndarray | None = None
        self._rec_frame: np.ndarray | None = None
        self._display_scale = 1.0
        self._rec_scale = 1.0

        self._engine = FaceEngine(logger=logger, threshold=config.fr_threshold)
        self._deepface = DeepFaceValidator(logger=logger)
        self._lbph_engine: LbphEngine | None = None
        self._users = UserStore(db)
        self._detections = DetectionStore(db)
        self._known_cache: list[tuple[int, str, np.ndarray]] = []

        self._auth_streak = 0
        self._auth_label: str | None = None
        self._unknown_streak = 0
        self._alert_cooldown_until = 0.0
        self._profiles_reload_after = 0.0
        self._last_overlays: list[tuple[int, int, int, int, str, tuple[int, int, int]]] = []
        self._last_loaded_encodings: int | None = None
        self._last_frame_for_unknown: np.ndarray | None = None
        self._already_authorized: set[str] = set()
        self._spoof_check_counter = 0
        self._deepface_cache: dict[str, bool] = {}
        self._reconnect_attempts = 0
        self._want_running = False
        self._known_signature: tuple[tuple[int, str | None, bool], ...] | None = None
        self._missing_encoding_attempted: set[int] = set()

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        header_row = QHBoxLayout()
        header = QLabel("Live camera")
        header.setObjectName("H1")
        header_row.addWidget(header, 0)
        header_row.addStretch(1)
        self._chip = QLabel("IDLE")
        self._chip.setObjectName("Chip")
        header_row.addWidget(self._chip, 0)
        root.addLayout(header_row)

        stage = QFrame()
        stage.setObjectName("GlassPanel")
        stage_layout = QVBoxLayout(stage)
        stage_layout.setContentsMargins(20, 20, 20, 20)
        stage_layout.setSpacing(16)

        self._video = QLabel()
        self._video.setMinimumHeight(580)
        self._video.setAlignment(Qt.AlignCenter)
        self._video.setStyleSheet(
            "background-color: rgba(7, 11, 20, 0.8); border: 1px solid rgba(0, 209, 255, 0.2); border-radius: 12px;"
        )
        stage_layout.addWidget(self._video, 1)
        root.addWidget(stage, 1)

        controls = QFrame()
        controls.setObjectName("GlassPanel")
        cl = QHBoxLayout(controls)
        cl.setContentsMargins(24, 20, 24, 20)
        cl.setSpacing(16)
        self._status = QLabel("STOPPED")
        self._status.setObjectName("Muted")
        self._status.setStyleSheet("font-weight: 600; font-size: 14px; letter-spacing: 1px;")
        self._light = QLabel("LIGHT: OFF")
        self._light.setObjectName("ChipWarn")
        self._spoof = QLabel("SPOOF: --")
        self._spoof.setObjectName("Muted")
        self._btn_toggle = QPushButton("Start camera")
        self._btn_toggle.clicked.connect(self._toggle_camera)
        cl.addWidget(self._status, 1)
        cl.addWidget(self._spoof, 0)
        cl.addWidget(self._light, 0)
        cl.addWidget(self._btn_toggle)
        root.addWidget(controls, 0)

    def _toggle_camera(self) -> None:
        if self._cap is None:
            self.start()
        else:
            self.stop()

    def start(self) -> None:
        if self._cap is not None:
            return
        self._want_running = True
        self._btn_toggle.setEnabled(False)
        self._status.setText("Opening camera...")
        self._reload_known()
        src = self._config.rtsp_url
        opened = open_camera(int(src)) if src.isdigit() else open_camera(src)
        self._cap = opened.cap
        if self._cap is None:
            self._status.setText("Camera open failed")
            self._set_chip("ERROR", "ChipBad")
            self._want_running = False
            self._btn_toggle.setText("Start camera")
            self._btn_toggle.setEnabled(True)
            self._logger.error("Camera open failed (backend=%s): %s", opened.backend, opened.error)
            return
        self._status.setText("Running")
        self._set_chip("LIVE", "ChipGood")
        self._logger.info("Camera opened (backend=%s, src=%s)", opened.backend, src)
        self._profiles_reload_after = 0.0
        self._stall_count = 0
        self._reconnect_attempts = 0
        self._known_signature = None
        interval_ms = max(16, int(1000 / max(1, self._config.camera_fps_target)))
        self._timer.start(interval_ms)
        self._rec_timer.start(500)
        self._btn_toggle.setText("Stop camera")
        self._btn_toggle.setEnabled(True)

    def stop(self) -> None:
        self._want_running = False
        self._timer.stop()
        self._rec_timer.stop()
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        self._status.setText("Stopped")
        self._set_chip("IDLE", "Chip")
        self._set_light(False)
        self._auth_streak = 0
        self._auth_label = None
        self._unknown_streak = 0
        self._already_authorized.clear()
        self._deepface_cache.clear()
        self._reconnect_attempts = 0
        self._btn_toggle.setText("Start camera")
        self._btn_toggle.setEnabled(True)

    def _set_chip(self, text: str, object_name: str) -> None:
        self._chip.setText(text)
        self._chip.setObjectName(object_name)
        self._chip.style().unpolish(self._chip)
        self._chip.style().polish(self._chip)

    def _reload_known(self) -> None:
        users = self._users.list_users()
        signature = tuple((u.id, u.face_image_path, u.face_encoding is not None) for u in users)
        if signature == self._known_signature:
            return

        self._known_cache.clear()
        if self._engine.has_face_recognition:
            for u in users:
                if u.face_encoding is None and u.face_image_path and u.id not in self._missing_encoding_attempted:
                    self._missing_encoding_attempted.add(u.id)
                    img = cv2.imread(u.face_image_path)
                    if img is not None:
                        try:
                            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
                            enc = self._engine.extract_encoding(rgb)
                            if enc is not None:
                                self._users.upsert_face(user_id=u.id, encoding=enc, image_path=u.face_image_path)
                        except Exception:
                            pass
            users = self._users.list_users()
            signature = tuple((u.id, u.face_image_path, u.face_encoding is not None) for u in users)
        for u in users:
            if u.face_encoding is not None:
                self._known_cache.append((u.id, u.label, u.face_encoding))
        if not self._engine.has_face_recognition:
            try:
                self._lbph_engine = LbphEngine(logger=self._logger)
                known = [LbphKnown(user_id=u.id, label=u.label, image_path=u.face_image_path) for u in users if u.face_image_path]
                self._lbph_engine.train_from_photos(known)
            except Exception as ex:
                self._lbph_engine = None
                self._logger.warning("LBPH init/train failed: %s", ex)
        loaded = len(self._known_cache)
        if self._last_loaded_encodings != loaded:
            self._last_loaded_encodings = loaded
            self._logger.info("Loaded %d encodings (face_recognition=%s, lbph=%s, deepface=%s)",
                              loaded, self._engine.has_face_recognition,
                              self._lbph_engine is not None, "lazy")
        if loaded == 0 and users:
            self._status.setText("Profiles found but no encodings yet (enroll again with face centered).")
        elif loaded == 0 and not users:
            self._status.setText("No users enrolled. Go to Face Recognition and enroll your face.")
        self._known_signature = signature

    def _set_light(self, on: bool) -> None:
        if self._plc:
            self._plc.set_light(on)
        else:
            if on:
                self._light.setText("LIGHT: ON")
                self._light.setObjectName("ChipGood")
            else:
                self._light.setText("LIGHT: OFF")
                self._light.setObjectName("ChipWarn")
            self._light.style().unpolish(self._light)
            self._light.style().polish(self._light)

    def _tick(self) -> None:
        import time
        now = time.time()
        if now >= self._profiles_reload_after:
            self._profiles_reload_after = now + 20.0
            self._reload_known()

        if self._cap is None:
            return
        ok, frame = safe_read(self._cap, max_retries=1, retry_sleep_s=0.0)
        if not ok or frame is None:
            self._stall_count += 1
            if self._stall_count >= 10:
                self._timer.stop()
                self._rec_timer.stop()
                self._set_chip("STALL", "ChipWarn")
                self._status.setText("Camera stalled - auto-reconnecting...")
                self._auto_reconnect()
            return
        self._stall_count = 0
        self._frame_idx += 1

        h_raw, w_raw = frame.shape[:2]
        scale = min(960.0 / w_raw, 540.0 / h_raw, 1.0)
        if scale < 1.0:
            display = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        else:
            display = frame
        self._display_scale = scale

        self._display_frame = display
        if self._frame_idx % 8 == 0:
            rec_h = min(360, h_raw)
            scale_rec = rec_h / h_raw
            self._rec_frame = cv2.resize(frame, None, fx=scale_rec, fy=scale_rec, interpolation=cv2.INTER_AREA)
            self._rec_scale = scale_rec

        if self._plc:
            self._plc.check_light_timer()
            if self._plc.is_light_on:
                self._light.setText(f"LIGHT: ON ({self._plc.light_remaining:.0f}s)")
                self._light.setObjectName("ChipGood")
            else:
                self._light.setText("LIGHT: OFF")
                self._light.setObjectName("ChipWarn")
            self._light.style().unpolish(self._light)
            self._light.style().polish(self._light)

        self._draw_overlays(display)

        rgb_display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_display.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_display.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
        pix = QPixmap.fromImage(qimg)
        self._video.setPixmap(pix.scaled(self._video.size(), Qt.KeepAspectRatio, Qt.FastTransformation))

    def _tick_recognition(self) -> None:
        if self._rec_frame is None:
            return
        frame = self._rec_frame
        self._last_frame_for_unknown = frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb, dtype=np.uint8)

        if self._engine.has_face_recognition:
            results = self._engine.identify_all(rgb, self._known_cache)
            self._apply_face_results(results, rgb, frame)
        elif self._lbph_engine is not None:
            user_id, label, conf = self._lbph_engine.predict(frame)
            if user_id is not None and conf >= self._config.confidence_min:
                if self._auth_label == label:
                    self._auth_streak += 1
                else:
                    self._auth_label = label
                    self._auth_streak = 1
                    self._already_authorized.discard(label)
                self._unknown_streak = 0
                if self._auth_streak >= self._config.multiframes_required and label not in self._already_authorized:
                    self._already_authorized.add(label)
                    self._on_authorized(user_id, label, conf, "lbph", frame)
            else:
                self._auth_streak = 0
                self._auth_label = None
                self._already_authorized.clear()
                self._unknown_streak += 1
                if self._unknown_streak >= self._config.multiframes_required:
                    self._on_unknown(frame)

    def _auto_reconnect(self) -> None:
        if not self._want_running:
            return
        if not hasattr(self, '_reconnect_attempts'):
            self._reconnect_attempts = 0
        self._reconnect_attempts += 1
        if self._reconnect_attempts > 5:
            self._status.setText("Max reconnections reached. Click Start.")
            self._set_chip("ERROR", "ChipBad")
            self._want_running = False
            self._btn_toggle.setText("Start camera")
            self._btn_toggle.setEnabled(True)
            return
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        src = self._config.rtsp_url
        opened = open_camera(int(src)) if src.isdigit() else open_camera(src)
        self._cap = opened.cap
        if self._cap is None:
            self._status.setText(f"Reconnect #{self._reconnect_attempts} failed")
            QTimer.singleShot(5000, self._auto_reconnect)
        else:
            self._reconnect_attempts = 0
            self._stall_count = 0
            interval_ms = max(1, int(1000 / max(1, self._config.camera_fps_target)))
            self._timer.start(interval_ms)
            self._rec_timer.start(500)
            self._status.setText("Reconnected")
            self._set_chip("LIVE", "ChipGood")
            self._btn_toggle.setText("Stop camera")
            self._btn_toggle.setEnabled(True)
            self._logger.info("Camera auto-reconnected")

    def _apply_face_results(self, results, rgb_frame: np.ndarray | None = None,
                            bgr_frame: np.ndarray | None = None) -> None:
        overlays: list[tuple[int, int, int, int, str, tuple[int, int, int]]] = []
        any_known = False
        any_unknown = False
        best_known = None
        for r in results:
            if r.box is None:
                continue
            left, top, right, bottom = r.box
            if r.user_id is not None and r.confidence >= self._config.confidence_min:
                any_known = True
                label = f"{r.label} ({r.confidence:.2f})"
                color = (80, 255, 140)
                if best_known is None or r.confidence > best_known.confidence:
                    best_known = r
            else:
                any_unknown = True
                label = "UNKNOWN"
                color = (60, 80, 255)
            overlays.append((left, top, right, bottom, label, color))
        self._last_overlays = overlays

        if any_known and best_known is not None and rgb_frame is not None:
            if self._auth_label == best_known.label:
                if self._auth_streak < self._config.multiframes_required * 2:
                    self._auth_streak += 1
            else:
                self._auth_label = best_known.label
                self._auth_streak = 1
                self._already_authorized.discard(best_known.label)
            self._unknown_streak = 0

            if self._auth_streak >= self._config.multiframes_required and best_known.label not in self._already_authorized:
                self._spoof_check_counter += 1
                skip_checks = self._spoof_check_counter % 5 != 0
                if not skip_checks:
                    spoofed, spoof_score, spoof_reason = detect_spoof(rgb_frame)
                    self._spoof.setText(f"SPOOF: {spoof_score:.2f} ({'FAKE' if spoofed else 'REAL'})")
                    if spoofed:
                        self._logger.warning("Spoof detected: %s (score=%.2f)", spoof_reason, spoof_score)
                        return
                if self._deepface.is_available and best_known.label not in self._deepface_cache:
                    self._deepface_cache[best_known.label] = True
                    try:
                        user_row = self._users.list_users()
                        user_path = None
                        for u in user_row:
                            if u.id == best_known.user_id and u.face_image_path:
                                user_path = u.face_image_path
                                break
                        if user_path:
                            df_ok, df_conf = self._deepface.verify(rgb_frame, user_path)
                            if not df_ok or df_conf < self._config.confidence_min:
                                self._logger.warning("DeepFace rejected match for %s (conf=%.2f)", best_known.label, df_conf)
                                self._deepface_cache[best_known.label] = False
                                return
                    except Exception:
                        pass

                self._already_authorized.add(best_known.label)
                self._on_authorized(best_known.user_id, best_known.label, best_known.confidence,
                                    "face_recognition", bgr_frame)

        elif any_unknown:
            self._auth_streak = 0
            self._auth_label = None
            self._already_authorized.clear()
            self._unknown_streak += 1
            if self._unknown_streak >= self._config.multiframes_required:
                self._on_unknown(bgr_frame if bgr_frame is not None else self._last_frame_for_unknown)
        else:
            self._auth_streak = 0
            self._auth_label = None
            self._already_authorized.clear()
            self._unknown_streak = 0

    def _draw_overlays(self, bgr_frame: np.ndarray) -> None:
        factor = self._display_scale / max(self._rec_scale, 1e-6)
        for left, top, right, bottom, label, color in self._last_overlays:
            left = max(0, int(left * factor)); top = max(0, int(top * factor))
            right = max(0, int(right * factor)); bottom = max(0, int(bottom * factor))
            cv2.rectangle(bgr_frame, (left, top), (right, bottom), color, 2)
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
            y0 = max(0, top - th - 10)
            cv2.rectangle(bgr_frame, (left, y0), (left + tw + 10, y0 + th + 10), color, -1)
            cv2.putText(bgr_frame, label, (left + 5, y0 + th + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

    def _on_authorized(self, user_id: int, label: str, confidence: float,
                        engine: str, bgr_frame: np.ndarray | None = None) -> None:
        self._status.setText(f"AUTHORIZED: {label} ({confidence:.2f})")
        self._set_light(True)
        self._set_chip("AUTHORIZED", "ChipGood")

        self._detections.add(
            DetectionEvent(
                type="authorized",
                user_id=user_id,
                confidence=confidence,
                capture_path=None,
                risk_level="low",
                details={"mode": self._config.mode, "engine": engine},
            )
        )
        self._logger.info("Authorized: %s (conf=%.2f, engine=%s)", label, confidence, engine)
        if self._plc:
            self._plc.set_light(True)

        import time
        ts = time.strftime("%Y%m%d_%H%M%S")
        alert_msg = f"AUTHORIZED: {label} | conf={confidence:.2f} | {ts}"
        if self._alerts:
            self._alerts.send_alert(alert_msg)

    def _on_unknown(self, bgr_frame: np.ndarray | None) -> None:
        import time
        now = time.time()
        if now < self._alert_cooldown_until:
            return
        self._alert_cooldown_until = now + 10.0

        out = None
        if bgr_frame is not None:
            Path("captures").mkdir(parents=True, exist_ok=True)
            ts = time.strftime("%Y%m%d_%H%M%S")
            out = Path("captures") / f"unknown_{ts}.jpg"
            cv2.imwrite(str(out), bgr_frame)

        self._set_light(False)
        self._status.setText("UNKNOWN DETECTED")
        self._set_chip("UNKNOWN", "ChipBad")

        self._detections.add(
            DetectionEvent(
                type="unknown",
                user_id=None,
                confidence=0.0,
                capture_path=str(out) if out is not None else None,
                risk_level="high",
                details={"mode": self._config.mode, "capture": out.name if out is not None else None},
            )
        )
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        alert_msg = f"UNKNOWN DETECTED | {ts} | risk=HIGH"
        if self._alerts:
            self._alerts.send_alert(alert_msg, str(out) if out else None)
        if out is not None:
            self._logger.warning("Unknown detected; capture saved: %s", out)

    def closeEvent(self, event) -> None:
        self.stop()
        return super().closeEvent(event)
