from __future__ import annotations

import logging
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget,
    QVBoxLayout, QWidget,
)

from smart_security_iot.core.config import AppConfig
from smart_security_iot.database.db import Database
from smart_security_iot.security.auth import AuthService
from smart_security_iot.services.alert_service import AlertService
from smart_security_iot.services.plc_service import PlcService
from smart_security_iot.services.watchdog import Watchdog
from smart_security_iot.ui.pages.access_control import AccessControlPage
from smart_security_iot.ui.pages.alerts_center import AlertsCenterPage
from smart_security_iot.ui.pages.dashboard import DashboardPage
from smart_security_iot.ui.pages.face_recognition import FaceRecognitionPage
from smart_security_iot.ui.pages.live_camera import LiveCameraPage
from smart_security_iot.ui.pages.settings import SettingsPage
from smart_security_iot.ui.theme import apply_control_center_theme

NAV_ITEMS = (
    ("Dashboard", "dashboard"),
    ("Camera", "live"),
    ("Faces", "faces"),
    ("Access", "access"),
    ("Alerts", "alerts"),
    ("Settings", "settings"),
)


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig, db: Database, auth: AuthService, logger: logging.Logger,
                 plc: PlcService | None = None, alerts: AlertService | None = None,
                 watchdog: Watchdog | None = None) -> None:
        super().__init__()
        self._config = config
        self._db = db
        self._auth = auth
        self._logger = logger
        self._plc = plc
        self._alerts = alerts
        self._watchdog = watchdog

        self.setWindowTitle("Smart Security IoT")
        self.setMinimumSize(1180, 760)
        self.resize(1440, 860)
        apply_control_center_theme(self)

        root = QWidget()
        root_shell = QFrame()
        root_shell.setObjectName("AppShell")
        shell_layout = QHBoxLayout(root_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(root_shell, 1)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 22, 18, 18)
        sidebar_layout.setSpacing(6)

        title = QLabel("Smart Security")
        title.setObjectName("H2")
        subtitle = QLabel("IoT control center")
        subtitle.setObjectName("Muted")
        subtitle.setStyleSheet("font-size: 12px;")

        mode_badge = QLabel(f"MODE: {self._config.mode.upper()}")
        mode_badge.setObjectName("Chip")

        self._plc_badge = QLabel("PLC: --")
        self._plc_badge.setObjectName("ChipWarn")

        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(24)
        sidebar_layout.addWidget(mode_badge)
        sidebar_layout.addWidget(self._plc_badge)
        sidebar_layout.addSpacing(24)

        self._stack = QStackedWidget()

        kw = {"config": config, "db": db, "logger": logger}
        self._page_factories = {
            "dashboard": lambda: DashboardPage(**kw, plc=plc),
            "live": lambda: LiveCameraPage(**kw, plc=plc, alerts=alerts),
            "faces": lambda: FaceRecognitionPage(**kw),
            "access": lambda: AccessControlPage(**kw, plc=plc),
            "alerts": lambda: AlertsCenterPage(**kw),
            "settings": lambda: SettingsPage(**kw),
        }
        self._pages: dict[str, QWidget] = {}

        self._nav_buttons: dict[str, QPushButton] = {}

        def add_nav(label_text: str, key: str) -> None:
            btn = QPushButton(label_text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setObjectName("NavButton")
            btn.clicked.connect(lambda: self._navigate(key))
            sidebar_layout.addWidget(btn)
            self._nav_buttons[key] = btn

        for label_text, key in NAV_ITEMS:
            add_nav(label_text, key)

        sidebar_layout.addStretch(1)

        right = QFrame()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        topbar = QFrame()
        topbar.setObjectName("TopBar")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(26, 16, 26, 16)
        topbar_layout.setSpacing(16)

        self._status = QLabel("System ready")
        self._status.setObjectName("Muted")
        self._clock = QLabel("")
        self._clock.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._clock.setObjectName("Muted")

        self._session_label = QLabel("")
        self._session_label.setObjectName("ChipGood")

        topbar_layout.addWidget(self._status, 1)
        topbar_layout.addWidget(self._session_label, 0)
        topbar_layout.addWidget(self._clock, 0)

        right_layout.addWidget(topbar)

        content = QFrame()
        content.setObjectName("Content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(18, 18, 18, 18)
        content_layout.setSpacing(0)
        content_layout.addWidget(self._stack, 1)
        right_layout.addWidget(content, 1)

        shell_layout.addWidget(sidebar, 0)
        shell_layout.addWidget(right, 1)

        sidebar.setFixedWidth(220)
        self.setCentralWidget(root)
        self._navigate("dashboard")

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _tick(self) -> None:
        self._clock.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if self._plc:
            connected = self._plc.is_connected
            self._plc_badge.setText(f"PLC: {'CONNECTED' if connected else 'DISCONNECTED'}")
            self._plc_badge.setObjectName("ChipGood" if connected else "ChipBad")
            self._plc_badge.style().unpolish(self._plc_badge)
            self._plc_badge.style().polish(self._plc_badge)

        session = self._auth.session
        if session:
            rem = int(session.remaining // 60)
            self._session_label.setText(f"Session: {rem}min")
        else:
            self._session_label.setText("Session: --")

    def _navigate(self, key: str) -> None:
        page = self._pages.get(key)
        if page is None:
            factory = self._page_factories.get(key)
            if factory is None:
                return
            page = factory()
            self._pages[key] = page
            self._stack.addWidget(page)
        self._stack.setCurrentWidget(page)
        label = next((name for name, item_key in NAV_ITEMS if item_key == key), key)
        self._status.setText(label)
        for k, b in self._nav_buttons.items():
            b.setProperty("active", "true" if k == key else "false")
            b.style().unpolish(b)
            b.style().polish(b)
