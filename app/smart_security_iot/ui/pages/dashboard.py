from __future__ import annotations

import logging

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QVBoxLayout, QWidget

from smart_security_iot.core.config import AppConfig
from smart_security_iot.database.db import Database
from smart_security_iot.services.detections import DetectionStore
from smart_security_iot.services.plc_service import PlcService


class DashboardPage(QWidget):
    def __init__(self, config: AppConfig, db: Database, logger: logging.Logger, plc: PlcService | None = None) -> None:
        super().__init__()
        self._config = config
        self._db = db
        self._logger = logger
        self._plc = plc
        self._detections = DetectionStore(db)
        self._cards: dict[str, tuple[QLabel, QLabel, QLabel]] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        header_row = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setObjectName("H1")
        subtitle = QLabel("Live status and recent security activity")
        subtitle.setObjectName("Muted")
        subtitle.setStyleSheet("font-size: 13px;")
        header_row.addWidget(title, 0)
        header_row.addStretch(1)
        header_row.addWidget(subtitle, 0)
        root.addLayout(header_row)

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(20)
        root.addLayout(grid)

        self._ai_card = self._metric_card("AI Engine", "Ready", "Face recognition pipeline")
        self._cam_card = self._metric_card("Camera", "Configured", config.rtsp_url)
        self._plc_card = self._metric_card("PLC", "Disconnected", f"{config.plc_ip}:{config.plc_port}")
        self._recent_card = self._metric_card("Last Hour", "0", "detections")
        self._auth_card = self._metric_card("Authorized", "0", "total entries")
        self._unknown_card = self._metric_card("Unknown", "0", "total alerts")

        grid.addWidget(self._ai_card, 0, 0)
        grid.addWidget(self._cam_card, 0, 1)
        grid.addWidget(self._plc_card, 1, 0)
        grid.addWidget(self._recent_card, 1, 1)
        grid.addWidget(self._auth_card, 0, 2)
        grid.addWidget(self._unknown_card, 1, 2)

        recent_panel = QFrame()
        recent_panel.setObjectName("GlassPanel")
        recent_layout = QVBoxLayout(recent_panel)
        recent_layout.setContentsMargins(20, 18, 20, 20)
        recent_layout.setSpacing(12)

        recent_title = QLabel("Recent activity")
        recent_title.setObjectName("H2")
        self._recent_list = QListWidget()
        recent_layout.addWidget(recent_title)
        recent_layout.addWidget(self._recent_list, 1)
        root.addWidget(recent_panel, 1)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(4000)
        self._refresh()

    def _refresh(self) -> None:
        try:
            auth_count = self._detections.count_by_type("authorized")
            unknown_count = self._detections.count_by_type("unknown")
            total_recent = self._detections.count_since(60)

            self._set_card("ai", "Ready", "Face recognition available")
            self._set_card("camera", "Configured", self._config.rtsp_url)
            plc_status = "Connected" if (self._plc and self._plc.is_connected) else "Disconnected"
            self._set_card("plc", plc_status, f"{self._config.plc_ip}:{self._config.plc_port}")
            self._set_card("recent", str(total_recent), "detections in the last 60 minutes")
            self._set_card("authorized", str(auth_count), "total entries")
            self._set_card("unknown", str(unknown_count), "total alerts")

            self._recent_list.clear()
            rows = self._detections.list_all(limit=8)
            if not rows:
                self._recent_list.addItem("No detections yet")
            for row in rows:
                ts = str(row.get("created_at", ""))[:19]
                dtype = str(row.get("type", "event")).upper()
                user = str(row.get("user") or "Unknown")
                risk = str(row.get("risk_level", "n/a")).upper()
                self._recent_list.addItem(f"{ts}  |  {dtype}  |  {user}  |  {risk}")
        except Exception as ex:
            self._logger.debug("Dashboard refresh failed: %s", ex)

    def _set_card(self, key: str, value: str, hint: str) -> None:
        labels = self._cards.get(key)
        if labels is None:
            return
        _, value_label, hint_label = labels
        value_label.setText(value)
        hint_label.setText(hint)

    def _metric_card(self, title: str, value: str, hint: str) -> QFrame:
        card = QFrame()
        card.setObjectName("GlassPanel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)
        t = QLabel(title)
        t.setObjectName("Muted")
        t.setStyleSheet("font-weight: 700; font-size: 12px;")
        v = QLabel(value)
        v.setStyleSheet("font-size: 27px; font-weight: 800; color: #9FE7DB;")
        h = QLabel(hint)
        h.setObjectName("Muted")
        h.setStyleSheet("font-size: 12px;")
        h.setWordWrap(True)
        layout.addWidget(t)
        layout.addWidget(v)
        layout.addWidget(h)
        key = title.lower().split()[0]
        if title == "Last Hour":
            key = "recent"
        self._cards[key] = (t, v, h)
        return card
