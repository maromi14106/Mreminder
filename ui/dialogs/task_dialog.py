"""Task dialog module."""

from datetime import datetime

from PySide6.QtCore import QTime
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTimeEdit,
    QVBoxLayout,
)

from models.task import Task

DIALOG_WIDTH = 300
DIALOG_HEIGHT = 200


class TaskDialog(QDialog):
    """Dialog for adding or editing a task."""

    def __init__(self, parent: QDialog | None = None) -> None:
        """Initialize the task dialog."""
        super().__init__(parent)
        self.setWindowTitle("タスクの追加")
        self.resize(DIALOG_WIDTH, DIALOG_HEIGHT)

        self._title_edit = QLineEdit()
        self._time_edit = QTimeEdit()
        self._time_edit.setDisplayFormat("HH:mm")
        self._time_edit.setTime(QTime(9, 0))
        
        self._repeat_combo = QComboBox()
        self._repeat_combo.addItems(["一回", "毎日", "毎週"])
        
        self._enabled_check = QCheckBox("有効")
        self._enabled_check.setChecked(True)

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the UI layout."""
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        form_layout.addRow("タイトル:", self._title_edit)
        form_layout.addRow("時刻:", self._time_edit)
        form_layout.addRow("繰り返し:", self._repeat_combo)
        form_layout.addRow("", self._enabled_check)
        
        layout.addLayout(form_layout)
        layout.addWidget(self._button_box)
        
        self.setLayout(layout)

    def accept(self) -> None:
        """Validate before accepting."""
        if not self._title_edit.text().strip():
            QMessageBox.warning(self, "エラー", "タイトルを入力してください。")
            return
        super().accept()

    def get_task(self) -> Task:
        """Get the created task from dialog inputs.

        Returns:
            Task object.
        """
        now_str = datetime.now().isoformat()
        return Task(
            id=None,
            title=self._title_edit.text().strip(),
            remind_at=self._time_edit.time().toString("HH:mm"),
            repeat_type=self._repeat_combo.currentText(),
            enabled=self._enabled_check.isChecked(),
            created_at=now_str,
            updated_at=now_str,
        )
