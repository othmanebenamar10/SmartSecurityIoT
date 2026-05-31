from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from smart_security_iot.security.auth import AuthError, AuthService
from smart_security_iot.ui.theme import apply_control_center_theme


class LoginDialog(QDialog):
    def __init__(self, auth: AuthService) -> None:
        super().__init__()
        self._auth = auth

        self.setWindowTitle("Sign in")
        self.setModal(True)
        self.setMinimumWidth(460)
        apply_control_center_theme(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("Smart Security IoT")
        title.setObjectName("H2")
        subtitle = QLabel("Authentication required")
        subtitle.setObjectName("Muted")
        root.addWidget(title)
        root.addWidget(subtitle)

        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self._user = QLineEdit()
        self._pass = QLineEdit()
        self._pass.setEchoMode(QLineEdit.Password)
        form.addRow("Username", self._user)
        form.addRow("Password", self._pass)
        root.addLayout(form)

        self._status = QLabel("")
        self._status.setStyleSheet("color: rgba(255,120,120,200); font-weight: 700;")
        root.addWidget(self._status)

        btn = QPushButton("Sign in")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._login)
        root.addWidget(btn)

    def _login(self) -> None:
        try:
            self._auth.login(self._user.text(), self._pass.text())
            self.accept()
        except AuthError as ex:
            self._status.setText(str(ex))
