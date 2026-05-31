from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from smart_security_iot.core.config import AppConfig


def configure_logging(config: AppConfig) -> logging.Logger:
    logger = logging.getLogger("smart_security_iot")
    logger.setLevel(logging.DEBUG if config.env == "dev" else logging.INFO)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    log_dir = Path(config.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    logfile = log_dir / "smart_security_iot.log"

    file_handler = logging.handlers.RotatingFileHandler(
        logfile, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    console_handler.setLevel(logging.INFO)

    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
