from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _getenv(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key, default)
    if value is None:
        return None
    value = value.strip()
    return value if value else default


def _getenv_int(key: str, default: int) -> int:
    raw = _getenv(key, None)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _getenv_float(key: str, default: float) -> float:
    raw = _getenv(key, None)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class AppConfig:
    env: str
    mode: str
    db_path: str
    log_dir: str

    rtsp_url: str
    camera_fps_target: int

    admin_username: str
    admin_password: str
    session_timeout_min: int
    max_login_attempts: int
    lockout_min: int

    fr_threshold: float
    multiframes_required: int
    confidence_min: float

    plc_ip: str
    plc_port: int
    plc_light_coil: int
    light_on_seconds: int

    telegram_bot_token: str | None
    telegram_chat_id: str | None
    discord_webhook_url: str | None
    smtp_host: str | None
    smtp_port: int
    smtp_user: str | None
    smtp_pass: str | None
    smtp_to: str | None

    @staticmethod
    def load() -> "AppConfig":
        # Load .env from repo root if present.
        load_dotenv(override=False)

        env = _getenv("SSIOT_ENV", "dev") or "dev"
        mode = (_getenv("SSIOT_MODE", "test") or "test").lower()
        db_path = _getenv("SSIOT_DB_PATH", "app_data/smart_security_iot.db") or "app_data/smart_security_iot.db"
        log_dir = _getenv("SSIOT_LOG_DIR", "logs") or "logs"

        rtsp_url = _getenv("RTSP_URL", "0") or "0"
        camera_fps_target = _getenv_int("CAMERA_FPS_TARGET", 15)

        admin_username = _getenv("ADMIN_USERNAME", "admin") or "admin"
        admin_password = _getenv("ADMIN_PASSWORD", "ChangeMeNow!") or "ChangeMeNow!"
        session_timeout_min = _getenv_int("SESSION_TIMEOUT_MIN", 20)
        max_login_attempts = _getenv_int("MAX_LOGIN_ATTEMPTS", 5)
        lockout_min = _getenv_int("LOCKOUT_MIN", 10)

        fr_threshold = _getenv_float("FR_THRESHOLD", 0.40)
        multiframes_required = _getenv_int("MULTIFRAME_REQUIRED", 5)
        confidence_min = _getenv_float("CONFIDENCE_MIN", 0.70)

        plc_ip = _getenv("PLC_IP", "192.168.1.50") or "192.168.1.50"
        plc_port = _getenv_int("PLC_PORT", 502)
        plc_light_coil = _getenv_int("PLC_LIGHT_COIL", 1)
        light_on_seconds = _getenv_int("LIGHT_ON_SECONDS", 15)

        telegram_bot_token = _getenv("TELEGRAM_BOT_TOKEN", None)
        telegram_chat_id = _getenv("TELEGRAM_CHAT_ID", None)
        discord_webhook_url = _getenv("DISCORD_WEBHOOK_URL", None)
        smtp_host = _getenv("SMTP_HOST", None)
        smtp_port = _getenv_int("SMTP_PORT", 587)
        smtp_user = _getenv("SMTP_USER", None)
        smtp_pass = _getenv("SMTP_PASS", None)
        smtp_to = _getenv("SMTP_TO", None)

        # Normalize mode
        if mode not in ("test", "real"):
            mode = "test"

        # Ensure db path is relative to repo if relative string.
        db_path = str(Path(db_path))
        log_dir = str(Path(log_dir))

        return AppConfig(
            env=env,
            mode=mode,
            db_path=db_path,
            log_dir=log_dir,
            rtsp_url=rtsp_url,
            camera_fps_target=camera_fps_target,
            admin_username=admin_username,
            admin_password=admin_password,
            session_timeout_min=session_timeout_min,
            max_login_attempts=max_login_attempts,
            lockout_min=lockout_min,
            fr_threshold=fr_threshold,
            multiframes_required=multiframes_required,
            confidence_min=confidence_min,
            plc_ip=plc_ip,
            plc_port=plc_port,
            plc_light_coil=plc_light_coil,
            light_on_seconds=light_on_seconds,
            telegram_bot_token=telegram_bot_token,
            telegram_chat_id=telegram_chat_id,
            discord_webhook_url=discord_webhook_url,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_pass=smtp_pass,
            smtp_to=smtp_to,
        )
