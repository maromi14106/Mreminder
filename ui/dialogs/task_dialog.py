"""Task dialog module."""

from datetime import datetime

from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from core.schedule import calculate_initial_next_run, truncate_to_minute
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

        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(QDate.currentDate())

        self._time_edit = QTimeEdit()
        self._time_edit.setDisplayFormat("HH:mm")

        self._weekday_combo = QComboBox()
        self._weekday_combo.addItems(
            ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
        )

        self._repeat_combo = QComboBox()
        self._repeat_combo.addItems(["一回", "毎日", "毎週"])
        self._repeat_combo.currentIndexChanged.connect(self._on_repeat_changed)

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

            if task.weekday is not None and 0 <= task.weekday <= 6:
                self._weekday_combo.setCurrentIndex(task.weekday)

            if task.repeat_type == "一回" and task.next_run_at:
                try:
                    dt = datetime.fromisoformat(task.next_run_at)
                    self._date_edit.setDate(QDate(dt.year, dt.month, dt.day))
                except ValueError:
                    pass

            self._enabled_check.setChecked(task.enabled)
        else:
            self._time_edit.setTime(QTime(9, 0))

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)

        self._build_ui()
        self._on_repeat_changed()

    def _build_ui(self) -> None:
        """Build the UI layout."""
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        form_layout.addRow("タイトル:", self._title_edit)
        form_layout.addRow("繰り返し:", self._repeat_combo)

        self._date_row = form_layout.rowCount()
        form_layout.addRow("日付:", self._date_edit)

        self._weekday_row = form_layout.rowCount()
        form_layout.addRow("曜日:", self._weekday_combo)

        form_layout.addRow("時刻:", self._time_edit)
        form_layout.addRow("", self._enabled_check)

        layout.addLayout(form_layout)
        layout.addWidget(self._button_box)

        self.setLayout(layout)

    def _on_repeat_changed(self) -> None:
        """Update UI visibility based on repeat type."""
        repeat = self._repeat_combo.currentText()
        if repeat == "一回":
            self._date_edit.setVisible(True)
            self._weekday_combo.setVisible(False)
            self._set_row_visible(self._date_row, True)
            self._set_row_visible(self._weekday_row, False)
        elif repeat == "毎日":
            self._date_edit.setVisible(False)
            self._weekday_combo.setVisible(False)
            self._set_row_visible(self._date_row, False)
            self._set_row_visible(self._weekday_row, False)
        elif repeat == "毎週":
            self._date_edit.setVisible(False)
            self._weekday_combo.setVisible(True)
            self._set_row_visible(self._date_row, False)
            self._set_row_visible(self._weekday_row, True)

    def _set_row_visible(self, row: int, visible: bool) -> None:
        """Helper to show/hide a row in the form layout."""
        layout = self.layout()
        if layout and layout.count() > 0:
            form = layout.itemAt(0).layout()
            if isinstance(form, QFormLayout):
                label = form.itemAt(row, QFormLayout.ItemRole.LabelRole)
                if label and label.widget():
                    label.widget().setVisible(visible)

    def accept(self) -> None:
        """Validate before accepting."""
        if not self._title_edit.text().strip():
            QMessageBox.warning(self, "エラー", "タイトルを入力してください。")
            return

        repeat_type = self._repeat_combo.currentText()
        if repeat_type == "一回":
            qdate = self._date_edit.date()
            qtime = self._time_edit.time()
            target_dt = datetime(
                qdate.year(), qdate.month(), qdate.day(), qtime.hour(), qtime.minute()
            )
            now = truncate_to_minute(datetime.now())
            if target_dt <= now:
                is_same_time = False
                if (
                    self._task
                    and self._task.repeat_type == "一回"
                    and self._task.next_run_at
                ):
                    try:
                        old_dt = datetime.fromisoformat(self._task.next_run_at)
                        if truncate_to_minute(old_dt) == target_dt:
                            is_same_time = True
                    except ValueError:
                        pass

                if not is_same_time:
                    QMessageBox.warning(
                        self, "エラー", "未来の日時を指定してください。"
                    )
                    return

        super().accept()

    def get_task(self) -> Task:
        """Get the created or edited task from dialog inputs."""
        now_str = datetime.now().isoformat()
        now = truncate_to_minute(datetime.now())

        task_id = self._task.id if self._task else None
        created_at = self._task.created_at if self._task else now_str
        last_notified_at = self._task.last_notified_at if self._task else None
        snoozed_until = self._task.snoozed_until if self._task else None

        repeat_type = self._repeat_combo.currentText()
        qtime = self._time_edit.time()

        if repeat_type == "一回":
            qdate = self._date_edit.date()
            target_dt = datetime(
                qdate.year(), qdate.month(), qdate.day(), qtime.hour(), qtime.minute()
            )
            weekday = None
        elif repeat_type == "毎日":
            target_dt = datetime.combine(now.date(), datetime.min.time()).replace(
                hour=qtime.hour(), minute=qtime.minute()
            )
            weekday = None
        elif repeat_type == "毎週":
            target_dt = datetime.combine(now.date(), datetime.min.time()).replace(
                hour=qtime.hour(), minute=qtime.minute()
            )
            weekday = self._weekday_combo.currentIndex()
        else:
            target_dt = now
            weekday = None

        next_run = None
        if self._task and self._task.next_run_at:
            is_schedule_changed = False

            if self._task.repeat_type != repeat_type:
                is_schedule_changed = True
            elif self._task.remind_at != qtime.toString("HH:mm"):
                is_schedule_changed = True
            elif repeat_type == "毎週" and self._task.weekday != weekday:
                is_schedule_changed = True
            elif repeat_type == "一回":
                try:
                    old_dt = datetime.fromisoformat(self._task.next_run_at)
                    if truncate_to_minute(old_dt) != target_dt:
                        is_schedule_changed = True
                except ValueError:
                    is_schedule_changed = True

            if not is_schedule_changed:
                next_run = self._task.next_run_at

        if next_run is None:
            next_run = calculate_initial_next_run(now, target_dt, repeat_type, weekday)

        return Task(
            id=task_id,
            title=self._title_edit.text().strip(),
            remind_at=qtime.toString("HH:mm"),
            repeat_type=repeat_type,
            enabled=self._enabled_check.isChecked(),
            created_at=created_at,
            updated_at=now_str,
            last_notified_at=last_notified_at,
            snoozed_until=snoozed_until,
            next_run_at=next_run,
            weekday=weekday,
        )
