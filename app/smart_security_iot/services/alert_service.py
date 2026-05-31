from __future__ import annotations

import logging
import smtplib
import threading
import time
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import requests

from smart_security_iot.core.config import AppConfig


class AlertService:
    def __init__(self, config: AppConfig, logger: logging.Logger) -> None:
        self._config = config
        self._logger = logger
        self._cooldown_until: float = 0.0
        self._cooldown_seconds = 15

    def send_alert(self, message: str, image_path: str | None = None) -> None:
        now = time.time()
        if now < self._cooldown_until:
            return
        self._cooldown_until = now + self._cooldown_seconds

        self._logger.info("ALERT: %s", message)
        worker = threading.Thread(
            target=self._deliver_alert,
            args=(message, image_path),
            daemon=True,
            name="alert-delivery",
        )
        worker.start()

    def _deliver_alert(self, message: str, image_path: str | None = None) -> None:
        self._send_telegram(message, image_path)
        self._send_discord(message)
        self._send_smtp(message, image_path)
        self._send_windows_notification(message)

    def _send_telegram(self, message: str, image_path: str | None = None) -> None:
        token = self._config.telegram_bot_token
        chat_id = self._config.telegram_chat_id
        if not token or not chat_id:
            return
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
            if image_path and Path(image_path).exists():
                photo_url = f"https://api.telegram.org/bot{token}/sendPhoto"
                with open(image_path, "rb") as f:
                    requests.post(photo_url, data={"chat_id": chat_id}, files={"photo": f}, timeout=10)
        except Exception as ex:
            self._logger.debug("Telegram send failed: %s", ex)

    def _send_discord(self, message: str) -> None:
        webhook = self._config.discord_webhook_url
        if not webhook:
            return
        try:
            requests.post(webhook, json={"content": message}, timeout=5)
        except Exception as ex:
            self._logger.debug("Discord send failed: %s", ex)

    def _send_smtp(self, message: str, image_path: str | None = None) -> None:
        host = self._config.smtp_host
        port = self._config.smtp_port
        user = self._config.smtp_user
        pw = self._config.smtp_pass
        to = self._config.smtp_to
        if not all([host, port, user, pw, to]):
            return
        try:
            msg = MIMEMultipart()
            msg["Subject"] = "Smart Security IoT - Alerte"
            msg["From"] = user
            msg["To"] = to
            msg.attach(MIMEText(message, "plain", "utf-8"))
            if image_path and Path(image_path).exists():
                with open(image_path, "rb") as f:
                    img = MIMEImage(f.read())
                    img.add_header("Content-Disposition", "attachment", filename=Path(image_path).name)
                    msg.attach(img)
            with smtplib.SMTP(host, port, timeout=10) as s:
                s.starttls()
                s.login(user, pw)
                s.send_message(msg)
        except Exception as ex:
            self._logger.debug("SMTP send failed: %s", ex)

    @staticmethod
    def _send_windows_notification(message: str) -> None:
        try:
            from plyer import notification

            notification.notify(
                title="Smart Security IoT",
                message=message,
                timeout=5,
            )
        except Exception:
            return
