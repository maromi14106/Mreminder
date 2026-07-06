"""Task service module."""

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
