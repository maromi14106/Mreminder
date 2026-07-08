"""Notification engine module."""

from datetime import datetime, timedelta

from PySide6.QtCore import QObject, QTimer

from database.exceptions import TaskRepositoryError
from models.task import Task
from services.task_service import TaskService
from ui.notifications.notification_manager import NotificationManager

CHECK_INTERVAL_MS = 15000
SNOOZE_MINUTES = 5


class NotificationEngine(QObject):
    """Engine that checks for due tasks and manages notifications."""

    def __init__(self, task_service: TaskService) -> None:
        """Initialize the notification engine."""
        super().__init__()
        self._task_service = task_service
        self._manager = NotificationManager()

        self._manager.popup_completed.connect(self._on_popup_completed)
        self._manager.popup_snoozed.connect(self._on_popup_snoozed)

        self._timer = QTimer(self)
        self._timer.setInterval(CHECK_INTERVAL_MS)
        self._timer.timeout.connect(self._check_tasks)

    def start(self) -> None:
        """Start the notification engine."""
        self._timer.start()
        self._check_tasks()

    def _check_tasks(self) -> None:
        """Check for due tasks and show notifications."""
        try:
            now = datetime.now()
            due_tasks = self._task_service.get_due_tasks(now)

            for task in due_tasks:
                if task.id is None:
                    continue

                shown = self._manager.show_task(task)
                if shown:
                    notified_at = now.isoformat()
                    self._task_service.mark_notified(task.id, now)
                    task.last_notified_at = notified_at
                    task.snoozed_until = None

        except TaskRepositoryError as e:
            print(f"NotificationEngine Database Error: {e}")
        except Exception as e:
            print(f"NotificationEngine Unexpected Error: {e}")

    def _on_popup_completed(self, task: Task) -> None:
        """Handle when a user clicks 'Complete' on a popup."""
        try:
            self._task_service.complete_task(task, datetime.now())
        except TaskRepositoryError as e:
            print(f"NotificationEngine Database Error on complete: {e}")

    def _on_popup_snoozed(self, task: Task) -> None:
        """Handle when a user clicks 'Snooze' on a popup."""
        if task.id is None:
            return

        try:
            until = datetime.now() + timedelta(minutes=SNOOZE_MINUTES)
            self._task_service.snooze_task(task.id, until)
        except TaskRepositoryError as e:
            print(f"NotificationEngine Database Error on snooze: {e}")
