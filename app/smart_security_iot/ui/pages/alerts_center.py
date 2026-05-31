from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget

from smart_security_iot.core.config import AppConfig
from smart_security_iot.database.db import Database
from smart_security_iot.services.detections import DetectionStore


class AlertsCenterPage(QWidget):
    def __init__(self, config: AppConfig, db: Database, logger: logging.Logger) -> None:
        super().__init__()
        self._config = config
        self._db = db
        self._logger = logger
        self._detections = DetectionStore(db)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        header_row = QHBoxLayout()
        header = QLabel("Alerts")
        header.setObjectName("H1")
        header_row.addWidget(header, 0)
        header_row.addStretch(1)
        self._count_label = QLabel("0 ALERTS")
        self._count_label.setObjectName("Chip")
        header_row.addWidget(self._count_label, 0)
        root.addLayout(header_row)

        card = QFrame()
        card.setObjectName("GlassPanel")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(24, 24, 24, 24)
        cl.setSpacing(20)

        self._list = QListWidget()
        cl.addWidget(self._list, 1)

        btn_row = QHBoxLayout()
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.refresh)
        btn_row.addStretch(1)
        btn_row.addWidget(btn_refresh)
        cl.addLayout(btn_row)

        root.addWidget(card, 1)

        self.refresh()

    def refresh(self) -> None:
        self._list.clear()
        rows = self._detections.list_all(limit=200)
        self._count_label.setText(f"{len(rows)} alerts")
        for r in rows:
            ts = r.get("created_at", "")[:19] if r.get("created_at") else ""
            dtype = str(r.get("type", "?")).upper()
            user = str(r.get("user", "Unknown")) if r.get("user") else "Unknown"
            conf = float(r.get("confidence", 0)) if r.get("confidence") is not None else 0.0
            risk = str(r.get("risk_level", "N/A")).upper()
            self._list.addItem(f"[{ts}] {dtype} | {user} | conf={conf:.2f} | risk={risk}")
