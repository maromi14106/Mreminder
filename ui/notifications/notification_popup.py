"""Notification popup module."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from models.task import Task


class NotificationPopup(QWidget):
    """Custom popup widget for task notifications."""

    completed = Signal(Task)
    snoozed = Signal(Task)

    def __init__(self, task: Task) -> None:
        """Initialize the popup."""
        super().__init__()
        self._task = task

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.setFixedSize(280, 100)
        self.setObjectName("NotificationPopup")

        self.setStyleSheet("""
            #NotificationPopup {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #4c5052;
            }
        """)

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the UI layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)

        header = QLabel("リマインダー")
        header.setStyleSheet("font-weight: bold; font-size: 12px; color: #a0a0a0;")
        layout.addWidget(header)

        title = QLabel(self._task.title)
        title.setStyleSheet("font-size: 14px; margin-top: 5px; margin-bottom: 5px;")
        layout.addWidget(title)

        button_layout = QHBoxLayout()

        btn_complete = QPushButton("完了")
        btn_snooze = QPushButton("5分後")

        btn_complete.clicked.connect(self._on_complete)
        btn_snooze.clicked.connect(self._on_snooze)

        button_layout.addStretch()
        button_layout.addWidget(btn_snooze)
        button_layout.addWidget(btn_complete)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _on_complete(self) -> None:
        """Handle complete button click."""
        self.completed.emit(self._task)

    def _on_snooze(self) -> None:
        """Handle snooze button click."""
        self.snoozed.emit(self._task)

    @property
    def task(self) -> Task:
        """Get the associated task."""
        return self._task
