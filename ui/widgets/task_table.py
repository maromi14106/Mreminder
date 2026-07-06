"""Task table widget module."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)

from models.task import Task

COLUMN_COUNT = 5
COL_CHECK = 0
COL_TITLE = 1
COL_TIME = 2
COL_REPEAT = 3
COL_STATUS = 4

WIDTH_CHECK = 30
WIDTH_TIME = 100
WIDTH_REPEAT = 100
WIDTH_STATUS = 80


class TaskTable(QTableWidget):
    """Table widget for displaying tasks."""

    def __init__(self) -> None:
        """Initialize the task table."""
        super().__init__()

        self.setColumnCount(COLUMN_COUNT)
        self.setHorizontalHeaderLabels(["✔", "タイトル", "時刻", "繰り返し", "状態"])

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        header = self.horizontalHeader()
        header.setSectionResizeMode(COL_CHECK, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(COL_CHECK, WIDTH_CHECK)
        
        header.setSectionResizeMode(COL_TITLE, QHeaderView.ResizeMode.Stretch)
        
        header.setSectionResizeMode(COL_TIME, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(COL_TIME, WIDTH_TIME)
        
        header.setSectionResizeMode(COL_REPEAT, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(COL_REPEAT, WIDTH_REPEAT)
        
        header.setSectionResizeMode(COL_STATUS, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(COL_STATUS, WIDTH_STATUS)

    def refresh(self, tasks: list[Task]) -> None:
        """Refresh table with new tasks."""
        self.set_tasks(tasks)

    def set_tasks(self, tasks: list[Task]) -> None:
        """Set multiple tasks to the table."""
        self.clear_tasks()
        for task in tasks:
            self.add_task(task)

    def add_task(self, task: Task) -> None:
        """Add a single task to the table."""
        row = self.rowCount()
        self.insertRow(row)

        check_item = QTableWidgetItem("✔" if task.enabled else "")
        check_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, COL_CHECK, check_item)

        self.setItem(row, COL_TITLE, QTableWidgetItem(task.title))
        self.setItem(row, COL_TIME, QTableWidgetItem(task.remind_at))
        self.setItem(row, COL_REPEAT, QTableWidgetItem(task.repeat_type))
        
        status_text = "有効" if task.enabled else "無効"
        self.setItem(row, COL_STATUS, QTableWidgetItem(status_text))
        
        self.item(row, COL_TITLE).setData(Qt.ItemDataRole.UserRole, task)

    def clear_tasks(self) -> None:
        """Clear all tasks from the table."""
        self.setRowCount(0)

    def current_task(self) -> Task | None:
        """Get the currently selected task."""
        row = self.currentRow()
        if row < 0:
            return None
        return self.item(row, COL_TITLE).data(Qt.ItemDataRole.UserRole)

    def selected_task_id(self) -> int | None:
        """Get the ID of the currently selected task."""
        task = self.current_task()
        return task.id if task else None
