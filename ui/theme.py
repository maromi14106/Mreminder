"""Application theme module."""

DARK_THEME = """
QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    font-size: 10pt;
}

QMainWindow {
    background-color: #1e1e1e;
}

QMenuBar {
    background-color: #252526;
    color: #ffffff;
}

QMenuBar::item:selected {
    background-color: #333333;
}

QMenu {
    background-color: #252526;
    color: #ffffff;
    border: 1px solid #3f3f46;
}

QMenu::item:selected {
    background-color: #094771;
}

QToolBar {
    background-color: #252526;
    border-bottom: 1px solid #3f3f46;
    spacing: 6px;
}

QPushButton {
    background-color: #2d2d30;
    color: #ffffff;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    padding: 6px 10px;
}

QPushButton:hover {
    background-color: #3a3a3d;
}

QPushButton:pressed {
    background-color: #094771;
}

QTableWidget {
    background-color: #252526;
    alternate-background-color: #2d2d30;
    color: #ffffff;
    gridline-color: #3f3f46;
    border: 1px solid #3f3f46;
}

QHeaderView::section {
    background-color: #2d2d30;
    color: #ffffff;
    padding: 6px;
    border: 1px solid #3f3f46;
}

QLineEdit,
QTimeEdit,
QComboBox {
    background-color: #252526;
    color: #ffffff;
    border: 1px solid #3f3f46;
    border-radius: 4px;
    padding: 4px;
}

QStatusBar {
    background-color: #252526;
    color: #cccccc;
    border-top: 1px solid #3f3f46;
}

QDialog {
    background-color: #1e1e1e;
    color: #ffffff;
}

QMessageBox {
    background-color: #1e1e1e;
    color: #ffffff;
}
"""
