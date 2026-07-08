"""Task service module."""

from datetime import datetime, timedelta

from core.schedule import calculate_next_run_after_completion
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
        if task.repeat_type not in ("一回", "毎日", "毎週"):
            raise ValueError(f"invalid repeat_type: {task.repeat_type}")

        if task.repeat_type == "毎週":
            if task.weekday is None or not (0 <= task.weekday <= 6):
                raise ValueError("weekday must be 0-6 for 毎週")
        else:
            task.weekday = None

        if task.next_run_at is None:
            raise ValueError("next_run_at cannot be None")

        try:
            datetime.fromisoformat(task.next_run_at)
        except ValueError:
            raise ValueError("invalid next_run_at format")

        if task.id is None:
            return self._repository.create(task)

        current = self._repository.find_by_id(task.id)
        if current:
            if (
                current.remind_at != task.remind_at
                or current.repeat_type != task.repeat_type
                or current.weekday != task.weekday
                or current.next_run_at != task.next_run_at
            ):
                task.last_notified_at = None
                task.snoozed_until = None

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
        else:
            if task.next_run_at is not None:
                next_run = calculate_next_run_after_completion(
                    completed_at, task.next_run_at, task.repeat_type
                )
                if next_run:
                    task.next_run_at = next_run

        task.snoozed_until = None
        task.updated_at = completed_at.isoformat()

        self.save_task(task)

    def quick_add(self, minutes: int, title: str = "クイックリマインダー") -> int:
        """Add a quick reminder task."""
        now = datetime.now().replace(microsecond=0)
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
            next_run_at=remind_time.isoformat(),
            weekday=None,
        )
        return self.save_task(task)

    def get_due_tasks(self, now: datetime) -> list[Task]:
        """Get tasks that are due for notification."""
        tasks = self.load_tasks()
        due_tasks = []

        for task in tasks:
            if not task.enabled:
                continue

            # Snooze condition overrides normal schedule
            if task.snoozed_until is not None:
                try:
                    snoozed_dt = datetime.fromisoformat(task.snoozed_until)
                    if now >= snoozed_dt:
                        due_tasks.append(task)
                        continue
                    else:
                        continue
                except ValueError:
                    pass

            if task.next_run_at is None:
                continue

            try:
                next_run_dt = datetime.fromisoformat(task.next_run_at)
            except ValueError:
                continue

            if next_run_dt <= now:
                if task.last_notified_at is None:
                    due_tasks.append(task)
                else:
                    try:
                        last_notified_dt = datetime.fromisoformat(task.last_notified_at)
                        if last_notified_dt < next_run_dt:
                            due_tasks.append(task)
                    except ValueError:
                        due_tasks.append(task)

        return due_tasks
