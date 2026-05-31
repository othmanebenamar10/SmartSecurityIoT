CONTROL_CENTER_QSS = r"""
QWidget {
  color: #F3F4EE;
  font-family: "Segoe UI", "Inter", Arial, sans-serif;
  font-size: 13px;
  letter-spacing: 0px;
}

QMainWindow,
QDialog,
QFrame#AppShell {
  background: #151718;
}

QFrame#Sidebar {
  background: #1B1E1F;
  border-right: 1px solid #303636;
}

QFrame#TopBar {
  background: #1B1E1F;
  border-bottom: 1px solid #303636;
}

QFrame#Content {
  background: #151718;
}

QFrame#Card,
QFrame#CardElevated,
QFrame#GlassPanel {
  background: #202423;
  border: 1px solid #343B39;
  border-radius: 8px;
}

QFrame#CardElevated {
  background: #242927;
}

QLabel#Muted {
  color: #A9B2AD;
}

QLabel#H1 {
  font-size: 26px;
  font-weight: 700;
  color: #F7F7F1;
}

QLabel#H2 {
  font-size: 18px;
  font-weight: 700;
  color: #F7F7F1;
}

QLabel#Chip,
QLabel#ChipGood,
QLabel#ChipWarn,
QLabel#ChipBad {
  padding: 6px 11px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 11px;
}

QLabel#Chip {
  color: #8ED8CC;
  background: #20312F;
  border: 1px solid #326C63;
}

QLabel#ChipGood {
  color: #98E6B5;
  background: #1F3328;
  border: 1px solid #3B7A51;
}

QLabel#ChipWarn {
  color: #FFD08A;
  background: #332C1F;
  border: 1px solid #8A6632;
}

QLabel#ChipBad {
  color: #FFAAA0;
  background: #3A2422;
  border: 1px solid #8D433B;
}

QPushButton {
  background: #2C3331;
  border: 1px solid #3B4542;
  border-radius: 8px;
  padding: 9px 14px;
  font-weight: 650;
  color: #F3F4EE;
}

QPushButton:hover {
  background: #34413E;
  border-color: #4E8179;
}

QPushButton:pressed {
  background: #24302E;
}

QPushButton:disabled {
  color: #69736F;
  background: #242827;
  border-color: #303635;
}

QPushButton#NavButton {
  text-align: left;
  padding: 11px 13px;
  border-radius: 8px;
  border: 1px solid transparent;
  background: transparent;
  color: #BAC3BE;
}

QPushButton#NavButton:hover {
  background: #242A29;
  border-color: #343B39;
  color: #F3F4EE;
}

QPushButton#NavButton[active="true"] {
  background: #263F3B;
  border: 1px solid #4E8179;
  color: #9FE7DB;
}

QLineEdit {
  background: #171A1B;
  border: 1px solid #343B39;
  border-radius: 8px;
  padding: 9px 11px;
  selection-background-color: #3F7E75;
  color: #F3F4EE;
}

QLineEdit:focus {
  border: 1px solid #65B8AC;
  background: #1B1F20;
}

QListWidget {
  background: #171A1B;
  border: 1px solid #343B39;
  border-radius: 8px;
  padding: 5px;
}

QListWidget::item {
  padding: 9px 10px;
  border-radius: 6px;
  color: #E9ECE7;
}

QListWidget::item:selected {
  background: #263F3B;
  color: #F7F7F1;
}

QListWidget::item:hover {
  background: #222928;
}

QTabWidget::pane {
  border: 1px solid #343B39;
  border-radius: 8px;
  background: #202423;
  padding: 12px;
}

QTabBar::tab {
  padding: 9px 16px;
  border-radius: 8px;
  margin-right: 6px;
  color: #A9B2AD;
  background: #1B1E1F;
  border: 1px solid #303636;
}

QTabBar::tab:selected {
  color: #9FE7DB;
  background: #263F3B;
  border-color: #4E8179;
}

QScrollBar:vertical {
  background: transparent;
  width: 8px;
  margin: 2px;
}

QScrollBar::handle:vertical {
  background: #48524F;
  border-radius: 4px;
  min-height: 24px;
}

QScrollBar::handle:vertical:hover {
  background: #6A7773;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
  height: 0;
  width: 0;
}
"""


def apply_control_center_theme(widget) -> None:
    widget.setStyleSheet(CONTROL_CENTER_QSS)
