"""Task service module."""

from datetime import datetime, timedelta

from database.repository import TaskRepository
from models.task import Task


class TaskService:
    """Service class for Task operations."""

    def __init__(self, repository: TaskRepository) -> None:
        """Initialize the TaskService."""
        self._repository = repository

    def load_tasks(self) -> list[Task]:
        """Load all tasks."""
        return self._repository.find_all()

    def get_task(self, task_id: int) -> Task | None:
        """Get a task by its ID."""
        return self._repository.find_by_id(task_id)

    def save_task(self, task: Task) -> int:
        """Save a task (create if ID is None, else update)."""
        if task.id is None:
            return self._repository.create(task)
        self._repository.update(task)
        return task.id

    def remove_task(self, task_id: int) -> None:
        """Remove a task by its ID."""
        self._repository.delete(task_id)

    def mark_notified(self, task_id: int, notified_at: datetime) -> None:
        """Mark a task as notified."""
        self._repository.mark_notified(task_id, notified_at.isoformat())

    def snooze_task(self, task_id: int, until: datetime) -> None:
        """Snooze a task until a specific time."""
        self._repository.snooze(task_id, until.isoformat())

    def complete_task(self, task: Task, completed_at: datetime) -> None:
        """Complete a task based on its repeat type."""
        if task.repeat_type == "一回":
            task.enabled = False

        task.snoozed_until = None
        task.updated_at = completed_at.isoformat()
        
        self.save_task(task)

    def quick_add(self, minutes: int, title: str = "クイックリマインダー") -> int:
        """Add a quick reminder task."""
        now = datetime.now()
        remind_time = now + timedelta(minutes=minutes)
        task = Task(
            id=None,
            title=title,
            remind_at=remind_time.strftime("%H:%M"),
            repeat_type="一回",
            enabled=True,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            last_notified_at=None,
            snoozed_until=None,
        )
        return self.save_task(task)

    def get_due_tasks(self, now: datetime) -> list[Task]:
        """Get tasks that are due for notification."""
        tasks = self.load_tasks()
        due_tasks = []

        now_time_str = now.strftime("%H:%M")
        now_date = now.date()

        for task in tasks:
            if not task.enabled:
                continue

            # Check snoozed tasks
            if task.snoozed_until is not None:
                try:
                    snoozed_until_dt = datetime.fromisoformat(task.snoozed_until)
                    if now >= snoozed_until_dt:
                        due_tasks.append(task)
                except ValueError:
                    # Ignore invalid date strings
                    continue
                continue

            # Check regular reminder tasks
            if task.remind_at == now_time_str:
                if task.last_notified_at is not None:
                    try:
                        last_notified_dt = datetime.fromisoformat(task.last_notified_at)
                        if last_notified_dt.date() == now_date:
                            # Already notified today
                            continue
                    except ValueError:
                        # Ignore invalid date strings and do not notify
                        continue
                        
                due_tasks.append(task)

        return due_tasks
