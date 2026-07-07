"""Theme module for the application."""

DARK_THEME = """
QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
}

QMenuBar {
    background-color: #2b2b2b;
    color: #ffffff;
}

QMenuBar::item:selected {
    background-color: #3b3b3b;
}

QMenu {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #3b3b3b;
}

QMenu::item:selected {
    background-color: #3b3b3b;
}

QToolBar {
    background-color: #2b2b2b;
    border: none;
}

QPushButton {
    background-color: #3b3b3b;
    color: #ffffff;
    border: 1px solid #555555;
    padding: 5px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #4b4b4b;
}

QPushButton:pressed {
    background-color: #1b1b1b;
}

QLineEdit, QComboBox, QSpinBox, QTimeEdit {
    background-color: #3b3b3b;
    color: #ffffff;
    border: 1px solid #555555;
    padding: 3px;
}

QTableView {
    background-color: #2b2b2b;
    color: #ffffff;
    alternate-background-color: #323232;
    selection-background-color: #4b4b4b;
    gridline-color: #555555;
}

QHeaderView::section {
    background-color: #3b3b3b;
    color: #ffffff;
    padding: 4px;
    border: 1px solid #555555;
}

QStatusBar {
    background-color: #2b2b2b;
    color: #ffffff;
}
"""
