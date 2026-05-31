from __future__ import annotations

import logging
import time

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from smart_security_iot.core.config import AppConfig
from smart_security_iot.database.db import Database
from smart_security_iot.services.plc_service import PlcService


class AccessControlPage(QWidget):
    def __init__(self, config: AppConfig, db: Database, logger: logging.Logger, plc: PlcService | None = None) -> None:
        super().__init__()
        self._config = config
        self._db = db
        self._logger = logger
        self._plc = plc

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        header = QLabel("Access")
        header.setObjectName("H1")
        root.addWidget(header)

        card = QFrame()
        card.setObjectName("GlassPanel")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(24, 24, 24, 24)
        cl.setSpacing(20)

        cl.addWidget(QLabel("Light control"))
        self._light_status = QLabel("LIGHT: OFF")
        self._light_status.setObjectName("ChipWarn")
        self._light_status.setStyleSheet("font-size: 13px; letter-spacing: 1px;")
        cl.addWidget(self._light_status)

        self._timer_label = QLabel("Remaining: --")
        self._timer_label.setObjectName("Muted")
        cl.addWidget(self._timer_label)

        btn_row = QHBoxLayout()
        self._btn_on = QPushButton("Turn ON")
        self._btn_off = QPushButton("Turn OFF")
        self._btn_on.clicked.connect(self._light_on)
        self._btn_off.clicked.connect(self._light_off)
        btn_row.addWidget(self._btn_on)
        btn_row.addWidget(self._btn_off)
        cl.addLayout(btn_row)

        cl.addWidget(QLabel("PLC connection"))
        self._plc_status = QLabel("PLC: Disconnected")
        self._plc_status.setObjectName("ChipBad")
        cl.addWidget(self._plc_status)
        self._btn_plc = QPushButton("Connect PLC")
        self._btn_plc.clicked.connect(self._toggle_plc)
        cl.addWidget(self._btn_plc)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("border: 1px solid rgba(0,220,255,30);")
        cl.addWidget(sep)

        cl.addWidget(QLabel("PLC logs"))
        self._plc_log = QLabel("No events")
        self._plc_log.setObjectName("Muted")
        self._plc_log.setWordWrap(True)
        cl.addWidget(self._plc_log)

        root.addWidget(card)
        root.addStretch(1)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._last_log_count = 0

    def _light_on(self) -> None:
        if self._plc:
            self._plc.set_light(True)
        self._update_ui()

    def _light_off(self) -> None:
        if self._plc:
            self._plc.set_light(False)
        self._update_ui()

    def _toggle_plc(self) -> None:
        if self._plc is None:
            return
        if self._plc.is_connected:
            self._plc.disconnect()
        else:
            self._plc.connect()
        self._update_ui()

    def _tick(self) -> None:
        self._update_ui()

    def _update_ui(self) -> None:
        if self._plc is None:
            self._plc_status.setText("PLC: Not configured")
            self._plc_status.setObjectName("ChipWarn")
        elif self._plc.is_connected:
            self._plc_status.setText("PLC: Connected")
            self._plc_status.setObjectName("ChipGood")
        else:
            self._plc_status.setText("PLC: Disconnected")
            self._plc_status.setObjectName("ChipBad")

        if self._plc and self._plc.is_light_on:
            self._light_status.setText("LIGHT: ON")
            self._light_status.setObjectName("ChipGood")
            rem = self._plc.light_remaining
            self._timer_label.setText(f"Auto-off in: {rem:.0f}s")
        else:
            self._light_status.setText("LIGHT: OFF")
            self._light_status.setObjectName("ChipWarn")
            self._timer_label.setText("Remaining: --")

        for w in (self._light_status, self._plc_status):
            w.style().unpolish(w)
            w.style().polish(w)
