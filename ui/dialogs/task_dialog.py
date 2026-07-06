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
    QWidget,
)

from models.task import Task

DIALOG_WIDTH = 300
DIALOG_HEIGHT = 200


class TaskDialog(QDialog):
    """Dialog for adding or editing a task."""

    def __init__(self, parent: QWidget | None = None, task: Task | None = None) -> None:
        """Initialize the task dialog."""
        super().__init__(parent)
        self._task = task
        
        title = "タスク編集" if task else "タスク追加"
        self.setWindowTitle(title)
        self.resize(DIALOG_WIDTH, DIALOG_HEIGHT)

        self._title_edit = QLineEdit()
        self._title_edit.setPlaceholderText("タスク名を入力")
        
        self._time_edit = QTimeEdit()
        self._time_edit.setDisplayFormat("HH:mm")
        
        self._repeat_combo = QComboBox()
        self._repeat_combo.addItems(["一回", "毎日", "毎週"])
        
        self._enabled_check = QCheckBox("有効")
        self._enabled_check.setChecked(True)

        if task:
            self._title_edit.setText(task.title)
            
            time_parts = task.remind_at.split(":")
            if len(time_parts) == 2:
                self._time_edit.setTime(QTime(int(time_parts[0]), int(time_parts[1])))
            else:
                self._time_edit.setTime(QTime(9, 0))
                
            combo_idx = self._repeat_combo.findText(task.repeat_type)
            if combo_idx >= 0:
                self._repeat_combo.setCurrentIndex(combo_idx)
                
            self._enabled_check.setChecked(task.enabled)
        else:
            self._time_edit.setTime(QTime(9, 0))

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
        """Get the created or edited task from dialog inputs."""
        now_str = datetime.now().isoformat()
        
        task_id = self._task.id if self._task else None
        created_at = self._task.created_at if self._task else now_str
        
        return Task(
            id=task_id,
            title=self._title_edit.text().strip(),
            remind_at=self._time_edit.time().toString("HH:mm"),
            repeat_type=self._repeat_combo.currentText(),
            enabled=self._enabled_check.isChecked(),
            created_at=created_at,
            updated_at=now_str,
        )
