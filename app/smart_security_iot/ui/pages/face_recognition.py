from __future__ import annotations

import logging
import time
from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox,
    QFileDialog, QPushButton, QTabWidget, QVBoxLayout, QWidget,
)

from smart_security_iot.ai.face_engine import FaceEngine
from smart_security_iot.core.config import AppConfig
from smart_security_iot.database.db import Database
from smart_security_iot.services.camera import open_camera, safe_read
from smart_security_iot.services.detections import DetectionStore
from smart_security_iot.services.users import UserStore


class FaceRecognitionPage(QWidget):
    def __init__(self, config: AppConfig, db: Database, logger: logging.Logger) -> None:
        super().__init__()
        self._config = config
        self._db = db
        self._logger = logger

        self._engine = FaceEngine(logger=logger, threshold=config.fr_threshold)
        self._users = UserStore(db)
        self._detections = DetectionStore(db)

        self._cap: cv2.VideoCapture | None = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._last_bgr = None
        self._last_boxes: list[tuple[int, int, int, int]] = []
        self._frame_idx = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        header = QLabel("Faces")
        header.setObjectName("H1")
        root.addWidget(header)

        tabs = QTabWidget()

        enroll_tab = QWidget()
        self._build_enroll_tab(enroll_tab)
        tabs.addTab(enroll_tab, "Enroll")

        history_tab = QWidget()
        self._build_history_tab(history_tab)
        tabs.addTab(history_tab, "History")

        root.addWidget(tabs, 1)

        self._tick_history()

    def _build_enroll_tab(self, parent: QWidget) -> None:
        root = QHBoxLayout(parent)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(14)

        left = QFrame()
        left.setObjectName("CardElevated")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(12, 12, 12, 12)
        ll.setSpacing(10)

        self._video = QLabel()
        self._video.setMinimumSize(620, 420)
        self._video.setAlignment(Qt.AlignCenter)
        self._video.setStyleSheet("background-color: rgba(0,0,0,140); border-radius: 12px;")
        ll.addWidget(self._video, 1)

        btns = QHBoxLayout()
        self._btn_toggle = QPushButton("Start webcam")
        self._btn_import = QPushButton("Import Photo")
        self._btn_toggle.clicked.connect(self._toggle_webcam)
        self._btn_import.clicked.connect(self.import_photo)
        btns.addWidget(self._btn_toggle)
        btns.addWidget(self._btn_import)
        ll.addLayout(btns)
        root.addWidget(left, 2)

        right = QFrame()
        right.setObjectName("CardElevated")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(16, 16, 16, 16)
        rl.setSpacing(10)

        self._list = QListWidget()
        self._list.setMinimumWidth(340)
        t = QLabel("Registered users")
        t.setObjectName("H2")
        rl.addWidget(t)
        rl.addWidget(self._list, 1)

        self._first = QLineEdit()
        self._first.setPlaceholderText("First name")
        self._last = QLineEdit()
        self._last.setPlaceholderText("Last name")
        rl.addWidget(self._first)
        rl.addWidget(self._last)

        self._status = QLabel("")
        self._status.setObjectName("Muted")
        rl.addWidget(self._status)

        self._btn_enroll = QPushButton("Enroll Face")
        self._btn_enroll.clicked.connect(self.enroll)
        rl.addWidget(self._btn_enroll)

        btn_row = QHBoxLayout()
        self._btn_remove = QPushButton("Remove Selected")
        self._btn_remove.clicked.connect(self._remove_selected)
        self._btn_refresh = QPushButton("Refresh")
        self._btn_refresh.clicked.connect(self.refresh)
        btn_row.addWidget(self._btn_remove)
        btn_row.addWidget(self._btn_refresh)
        rl.addLayout(btn_row)

        hint = QLabel("Select a user to update/remove, or fill names to create a new user.")
        hint.setObjectName("Muted")
        hint.setStyleSheet("font-size: 12px;")
        rl.addWidget(hint)
        rl.addStretch(0)
        root.addWidget(right, 1)

        self.refresh()

    def _build_history_tab(self, parent: QWidget) -> None:
        root = QVBoxLayout(parent)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(10)

        self._history_list = QListWidget()
        root.addWidget(self._history_list, 1)

        btn_refresh = QPushButton("Refresh History")
        btn_refresh.clicked.connect(self._tick_history)
        root.addWidget(btn_refresh)

    def _tick_history(self) -> None:
        self._history_list.clear()
        rows = self._detections.list_all(limit=100)
        for r in rows:
            ts = str(r.get("created_at", ""))[:19] if r.get("created_at") else ""
            dtype = str(r.get("type", "?")).upper()
            user = str(r.get("user", "?")) if r.get("user") else "?"
            conf = float(r.get("confidence", 0)) if r.get("confidence") is not None else 0.0
            risk = str(r.get("risk_level", "?")).upper()
            self._history_list.addItem(f"[{ts}] {dtype} | {user} | conf={conf:.2f} | risk={risk}")

    def refresh(self) -> None:
        self._list.clear()
        for u in self._users.list_users():
            has_face = "yes" if (u.face_encoding is not None or u.face_image_path) else "no"
            self._list.addItem(f"{u.id:04d} | {u.label} | face:{has_face}")

    def _remove_selected(self) -> None:
        uid = self._selected_user_id()
        if uid is None:
            self._status.setText("Select a user to remove")
            return
        reply = QMessageBox.question(self, "Confirm", "Remove this user and their face data?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        if self._users.delete_user(uid):
            self._status.setText(f"User {uid} removed")
            self.refresh()
        else:
            self._status.setText("Failed to remove user")

    def start(self) -> None:
        if self._cap is not None:
            return
        self._btn_toggle.setEnabled(False)
        self._status.setText("Opening webcam...")
        opened = open_camera(0)
        self._cap = opened.cap
        if self._cap is None:
            self._status.setText("Webcam open failed")
            self._btn_toggle.setEnabled(True)
            self._logger.error("Webcam open failed (backend=%s): %s", opened.backend, opened.error)
            return
        self._status.setText("Webcam running")
        self._btn_toggle.setText("Stop webcam")
        self._btn_toggle.setEnabled(True)
        self._timer.start(100)

    def stop(self) -> None:
        self._timer.stop()
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        self._status.setText("Stopped")
        self._btn_toggle.setText("Start webcam")

    def _toggle_webcam(self) -> None:
        if self._cap is None:
            self.start()
        else:
            self.stop()

    def _tick(self) -> None:
        if self._cap is None:
            return
        ok, frame = safe_read(self._cap, max_retries=1, retry_sleep_s=0.0)
        if not ok or frame is None:
            return
        self._last_bgr = frame
        self._frame_idx += 1
        if self._engine.has_face_recognition and (self._frame_idx % 5 == 0):
            try:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
                self._last_boxes = self._engine.detect_boxes(rgb)
            except Exception:
                self._last_boxes = []
        preview = frame.copy()
        if self._last_boxes:
            left, top, right, bottom = sorted(
                self._last_boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]), reverse=True
            )[0]
            cv2.rectangle(preview, (left, top), (right, bottom), (80, 255, 140), 2)
            cv2.putText(preview, "FACE DETECTED", (left, max(0, top - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 255, 140), 2)
        else:
            cv2.putText(preview, "NO FACE", (14, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (60, 80, 255), 2)
        self._render_bgr(preview)

    def import_photo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select a photo", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            self._status.setText("Failed to read image")
            return
        Path("captures").mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        imported = Path("captures") / f"import_{ts}{Path(path).suffix.lower()}"
        ok = cv2.imwrite(str(imported), img)
        self._last_bgr = img
        self._render_bgr(img)
        self._status.setText(f"Imported: {Path(path).name}" if ok else f"Imported (save failed)")

    def _render_bgr(self, bgr) -> None:
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
        pix = QPixmap.fromImage(qimg)
        self._video.setPixmap(pix.scaled(self._video.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def enroll(self) -> None:
        if not self._engine.can_enroll():
            self._status.setText("No face engine available. Install opencv-contrib-python or face_recognition.")
            return
        if self._last_bgr is None:
            self._status.setText("No frame")
            return
        first = (self._first.text() or "").strip()
        last = (self._last.text() or "").strip()
        selected_user_id = self._selected_user_id()
        creating_new = bool(first and last)
        updating_existing = selected_user_id is not None and not creating_new
        if not creating_new and not updating_existing:
            self._status.setText("Fill first/last to create, or select a user to update")
            return
        try:
            rgb = cv2.cvtColor(self._last_bgr, cv2.COLOR_BGR2RGB)
        except Exception as ex:
            self._status.setText(f"Image convert failed: {ex}")
            return
        rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
        enc = self._engine.extract_encoding(rgb)
        if enc is None and self._engine.has_face_recognition:
            try:
                boxes = self._engine.detect_boxes(rgb)
                if boxes:
                    left, top, right, bottom = sorted(
                        boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]), reverse=True
                    )[0]
                    pad = int(0.15 * max(right - left, bottom - top))
                    x0 = max(0, left - pad); y0 = max(0, top - pad)
                    x1 = min(rgb.shape[1], right + pad); y1 = min(rgb.shape[0], bottom + pad)
                    cropped = rgb[y0:y1, x0:x1]
                    cropped = np.ascontiguousarray(cropped, dtype=np.uint8)
                    enc = self._engine.extract_encoding(cropped)
            except Exception:
                pass
        if enc is None and self._engine.has_face_recognition:
            self._status.setText("No face detected. Move closer, face forward, better light, then retry.")
            return
        if creating_new:
            user_id = self._users.create_user(first_name=first, last_name=last)
            label = f"{last} {first}".strip()
        else:
            user_id = int(selected_user_id)
            label = self._selected_user_label() or "selected user"
        Path("captures").mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        out = Path("captures") / f"enroll_{user_id}_{ts}.jpg"
        if not cv2.imwrite(str(out), self._last_bgr):
            self._status.setText("Enroll failed: could not save capture")
            return
        try:
            self._users.upsert_face(user_id=user_id, encoding=enc, image_path=str(out))
        except Exception as ex:
            self._status.setText(f"Enroll failed: {ex}")
            return
        if creating_new:
            self._status.setText(f"Enrolled new user: {label}")
            self._first.setText(""); self._last.setText("")
        else:
            self._status.setText(f"Updated face for: {label}")
        self.refresh()

    def _selected_user_id(self) -> int | None:
        item = self._list.currentItem()
        if item is None:
            return None
        try:
            head = item.text().split("|", 1)[0].strip()
            return int(head)
        except Exception:
            return None

    def _selected_user_label(self) -> str | None:
        item = self._list.currentItem()
        if item is None:
            return None
        parts = [p.strip() for p in item.text().split("|")]
        return parts[1] if len(parts) >= 2 else None

    def closeEvent(self, event) -> None:
        self.stop()
        return super().closeEvent(event)
