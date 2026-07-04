from database.repository import TaskRepository
from models.task import Task


class TaskService:

    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def get_tasks(self) -> list[Task]:
        return self._repository.find_all()

    def get_task(self, task_id: int) -> Task | None:
        return self._repository.find_by_id(task_id)

    def add_task(self, task: Task) -> int:
        return self._repository.create(task)

    def update_task(self, task: Task) -> None:
        self._repository.update(task)

    def delete_task(self, task_id: int) -> None:
        self._repository.delete(task_id)
