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
            last_notified_at=cast(str | None, row["last_notified_at"]),
            snoozed_until=cast(str | None, row["snoozed_until"]),
            next_run_at=cast(str | None, row["next_run_at"]),
            weekday=cast(int | None, row["weekday"]),
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
                title, remind_at, repeat_type, enabled, created_at, updated_at, last_notified_at, snoozed_until, next_run_at, weekday
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    task.last_notified_at,
                    task.snoozed_until,
                    task.next_run_at,
                    task.weekday,
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
                updated_at = ?,
                last_notified_at = ?,
                snoozed_until = ?,
                next_run_at = ?,
                weekday = ?
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
                    task.last_notified_at,
                    task.snoozed_until,
                    task.next_run_at,
                    task.weekday,
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

    def mark_notified(self, task_id: int, notified_at: str) -> None:
        """Mark a task as notified at a specific time."""
        sql = """
            UPDATE tasks
            SET last_notified_at = ?,
                snoozed_until = NULL
            WHERE id = ?
        """
        try:
            self.execute(sql, (notified_at, task_id))
            self.commit()
        except sqlite3.Error as e:
            raise TaskRepositoryError(
                f"Failed to mark notified for task {task_id}."
            ) from e

    def snooze(self, task_id: int, snoozed_until: str) -> None:
        """Set a snooze time for a task."""
        sql = "UPDATE tasks SET snoozed_until = ? WHERE id = ?"
        try:
            self.execute(sql, (snoozed_until, task_id))
            self.commit()
        except sqlite3.Error as e:
            raise TaskRepositoryError(f"Failed to snooze task {task_id}.") from e
