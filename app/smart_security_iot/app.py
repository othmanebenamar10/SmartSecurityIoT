import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QDialog

from smart_security_iot.core.config import AppConfig
from smart_security_iot.core.logging import configure_logging
from smart_security_iot.core.paths import ensure_app_dirs
from smart_security_iot.database.db import Database
from smart_security_iot.security.auth import AuthService
from smart_security_iot.services.alert_service import AlertService
from smart_security_iot.services.plc_service import PlcService
from smart_security_iot.services.watchdog import Watchdog
from smart_security_iot.ui.login_dialog import LoginDialog
from smart_security_iot.ui.main_window import MainWindow


def main() -> int:
    config = AppConfig.load()
    ensure_app_dirs(config)
    logger = configure_logging(config)

    db = Database(Path(config.db_path))
    db.migrate()

    auth = AuthService(db, config, logger)
    auth.bootstrap_admin()

    plc = PlcService(config, logger)
    alerts = AlertService(config, logger)
    watchdog = Watchdog(logger, interval_s=10.0)

    if config.mode == "real":
        plc_ok = plc.connect()
        if plc_ok:
            logger.info("PLC connected automatically (real mode)")
        watchdog.register("plc", lambda: plc.is_connected, lambda: plc.connect())

    if watchdog.has_checks:
        watchdog.start()
        logger.info("Watchdog started")

    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("Smart Security IoT")
    app.setOrganizationName("Smart Security IoT")

    login = LoginDialog(auth=auth)
    if login.exec() != QDialog.Accepted:
        watchdog.stop()
        return 1

    window = MainWindow(config=config, db=db, auth=auth, logger=logger,
                        plc=plc, alerts=alerts, watchdog=watchdog)
    window.show()

    exit_code = app.exec()
    watchdog.stop()
    if plc:
        plc.disconnect()
    return exit_code
