"""Task repository module."""

import sqlite3
from typing import cast

from database.base_repository import BaseRepository
from database.database import Database
from database.exceptions import TaskRepositoryError
from models.task import Task


class TaskRepository(BaseRepository):
    """Repository for Task entity."""

    def __init__(self, db: Database) -> None:
        """Initialize the TaskRepository."""
        super().__init__(db)

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        """Convert a SQLite Row to a Task model."""
        return Task(
            id=cast(int, row["id"]),
            title=cast(str, row["title"]),
            remind_at=cast(str, row["remind_at"]),
            repeat_type=cast(str, row["repeat_type"]),
            enabled=bool(row["enabled"]),
            created_at=cast(str, row["created_at"]),
            updated_at=cast(str, row["updated_at"]),
        )

    def find_all(self) -> list[Task]:
        """Find all tasks."""
        sql = "SELECT * FROM tasks ORDER BY remind_at, id"
        try:
            cursor = self.execute(sql)
            return [self._row_to_task(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise TaskRepositoryError("Failed to fetch all tasks.") from e

    def find_by_id(self, task_id: int) -> Task | None:
        """Find a task by its ID."""
        sql = "SELECT * FROM tasks WHERE id = ?"
        try:
            cursor = self.execute(sql, (task_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_task(row)
        except sqlite3.Error as e:
            raise TaskRepositoryError(f"Failed to fetch task {task_id}.") from e

    def create(self, task: Task) -> int:
        """Create a new task."""
        sql = """
            INSERT INTO tasks (
                title, remind_at, repeat_type, enabled, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            cursor = self.execute(
                sql,
                (
                    task.title,
                    task.remind_at,
                    task.repeat_type,
                    int(task.enabled),
                    task.created_at,
                    task.updated_at,
                ),
            )
            self.commit()
            return cast(int, cursor.lastrowid)
        except sqlite3.Error as e:
            raise TaskRepositoryError("Failed to create task.") from e

    def update(self, task: Task) -> None:
        """Update an existing task."""
        if task.id is None:
            raise ValueError("Task ID cannot be None for update")

        sql = """
            UPDATE tasks
            SET title = ?,
                remind_at = ?,
                repeat_type = ?,
                enabled = ?,
                updated_at = ?
            WHERE id = ?
        """
        try:
            self.execute(
                sql,
                (
                    task.title,
                    task.remind_at,
                    task.repeat_type,
                    int(task.enabled),
                    task.updated_at,
                    task.id,
                ),
            )
            self.commit()
        except sqlite3.Error as e:
            raise TaskRepositoryError(f"Failed to update task {task.id}.") from e

    def delete(self, task_id: int) -> None:
        """Delete a task by its ID."""
        sql = "DELETE FROM tasks WHERE id = ?"
        try:
            self.execute(sql, (task_id,))
            self.commit()
        except sqlite3.Error as e:
            raise TaskRepositoryError(f"Failed to delete task {task_id}.") from e
