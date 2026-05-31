from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtWidgets import QFrame, QFormLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget

from smart_security_iot.core.config import AppConfig
from smart_security_iot.database.db import Database


class SettingsPage(QWidget):
    def __init__(self, config: AppConfig, db: Database, logger: logging.Logger) -> None:
        super().__init__()
        self._config = config
        self._db = db
        self._logger = logger

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        header = QLabel("Settings")
        header.setObjectName("H1")
        root.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(14)

        card = QFrame()
        card.setObjectName("GlassPanel")
        fl = QFormLayout(card)
        fl.setContentsMargins(24, 24, 24, 24)
        fl.setHorizontalSpacing(20)
        fl.setVerticalSpacing(16)

        self._rtsp = QLineEdit(config.rtsp_url)
        self._plc_ip = QLineEdit(config.plc_ip)
        self._plc_port = QLineEdit(str(config.plc_port))
        self._confidence = QLineEdit(str(config.confidence_min))
        self._multiframe = QLineEdit(str(config.multiframes_required))
        self._light_dur = QLineEdit(str(config.light_on_seconds))
        self._fr_threshold = QLineEdit(str(config.fr_threshold))
        self._telegram_token = QLineEdit(config.telegram_bot_token or "")
        self._telegram_chat = QLineEdit(config.telegram_chat_id or "")
        self._discord = QLineEdit(config.discord_webhook_url or "")
        self._smtp_host = QLineEdit(config.smtp_host or "")
        self._smtp_port = QLineEdit(str(config.smtp_port))
        self._smtp_user = QLineEdit(config.smtp_user or "")
        self._smtp_pass = QLineEdit(config.smtp_pass or "")
        self._smtp_to = QLineEdit(config.smtp_to or "")
        self._session_timeout = QLineEdit(str(config.session_timeout_min))

        pw_mode = QLineEdit.PasswordEchoOnEdit
        self._telegram_token.setEchoMode(pw_mode)
        self._smtp_pass.setEchoMode(pw_mode)

        fl.addRow("Camera (RTSP / index)", self._rtsp)
        fl.addRow("PLC IP", self._plc_ip)
        fl.addRow("PLC Port", self._plc_port)
        fl.addRow("Confidence Min (0-1)", self._confidence)
        fl.addRow("Multi-frame required", self._multiframe)
        fl.addRow("Light duration (s)", self._light_dur)
        fl.addRow("Face distance threshold", self._fr_threshold)
        fl.addRow("Session timeout (min)", self._session_timeout)
        fl.addRow("Telegram Bot Token", self._telegram_token)
        fl.addRow("Telegram Chat ID", self._telegram_chat)
        fl.addRow("Discord Webhook", self._discord)
        fl.addRow("SMTP Host", self._smtp_host)
        fl.addRow("SMTP Port", self._smtp_port)
        fl.addRow("SMTP User", self._smtp_user)
        fl.addRow("SMTP Pass", self._smtp_pass)
        fl.addRow("SMTP To", self._smtp_to)

        scroll_layout.addWidget(card)

        btn = QPushButton("Save to .env (project root)")
        btn.clicked.connect(self._save_env)
        scroll_layout.addWidget(btn)

        self._status = QLabel("Changes take effect after app restart. .env overrides all defaults.")
        self._status.setObjectName("Muted")
        scroll_layout.addWidget(self._status)
        scroll_layout.addStretch(1)
        scroll.setWidget(scroll_content)
        root.addWidget(scroll, 1)

    def _save_env(self) -> None:
        env_path = Path(".env")
        try:
            self._validate()
            lines = []
            lines.append(f"RTSP_URL={self._rtsp.text()}")
            lines.append(f"PLC_IP={self._plc_ip.text()}")
            lines.append(f"PLC_PORT={self._plc_port.text()}")
            lines.append(f"CONFIDENCE_MIN={self._confidence.text()}")
            lines.append(f"MULTIFRAME_REQUIRED={self._multiframe.text()}")
            lines.append(f"LIGHT_ON_SECONDS={self._light_dur.text()}")
            lines.append(f"FR_THRESHOLD={self._fr_threshold.text()}")
            lines.append(f"SESSION_TIMEOUT_MIN={self._session_timeout.text()}")
            lines.append(f"TELEGRAM_BOT_TOKEN={self._telegram_token.text()}")
            lines.append(f"TELEGRAM_CHAT_ID={self._telegram_chat.text()}")
            lines.append(f"DISCORD_WEBHOOK_URL={self._discord.text()}")
            lines.append(f"SMTP_HOST={self._smtp_host.text()}")
            lines.append(f"SMTP_PORT={self._smtp_port.text()}")
            lines.append(f"SMTP_USER={self._smtp_user.text()}")
            lines.append(f"SMTP_PASS={self._smtp_pass.text()}")
            lines.append(f"SMTP_TO={self._smtp_to.text()}")
            env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            self._logger.info("Settings saved to .env")
            self._status.setText("Saved to .env. Restart the app to apply changes.")
        except Exception as ex:
            self._logger.error("Failed to save .env: %s", ex)
            self._status.setText(f"Save failed: {ex}")

    def _validate(self) -> None:
        int_fields = {
            "PLC Port": self._plc_port.text(),
            "Multi-frame required": self._multiframe.text(),
            "Light duration": self._light_dur.text(),
            "SMTP Port": self._smtp_port.text(),
            "Session timeout": self._session_timeout.text(),
        }
        for label, value in int_fields.items():
            if int(value) < 0:
                raise ValueError(f"{label} must be positive")

        float_fields = {
            "Confidence Min": self._confidence.text(),
            "Face distance threshold": self._fr_threshold.text(),
        }
        for label, value in float_fields.items():
            number = float(value)
            if number < 0:
                raise ValueError(f"{label} must be positive")
