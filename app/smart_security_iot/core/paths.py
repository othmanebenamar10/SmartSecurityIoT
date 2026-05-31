from __future__ import annotations

from pathlib import Path

from smart_security_iot.core.config import AppConfig


def ensure_app_dirs(config: AppConfig) -> None:
    Path(config.log_dir).mkdir(parents=True, exist_ok=True)
    Path(config.db_path).parent.mkdir(parents=True, exist_ok=True)
    Path("captures").mkdir(parents=True, exist_ok=True)


CAPTURES_DIR = Path("captures").resolve()
