import sqlite3
from typing import cast

from database.base_repository import BaseRepository
from database.database import Database
from models.task import Task


class TaskRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)

    def _row_to_task(self, row: sqlite3.Row) -> Task:
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
        sql = "SELECT * FROM tasks"
        cursor = self.execute(sql)
        return [self._row_to_task(row) for row in cursor.fetchall()]

    def find_by_id(self, task_id: int) -> Task | None:
        sql = "SELECT * FROM tasks WHERE id = ?"
        cursor = self.execute(sql, (task_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_task(row)

    def create(self, task: Task) -> int:
        sql = """
            INSERT INTO tasks (
                title, remind_at, repeat_type, enabled, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
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

    def update(self, task: Task) -> None:
        if task.id is None:
            return

        sql = """
            UPDATE tasks
            SET title = ?,
                remind_at = ?,
                repeat_type = ?,
                enabled = ?,
                updated_at = ?
            WHERE id = ?
        """
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

    def delete(self, task_id: int) -> None:
        sql = "DELETE FROM tasks WHERE id = ?"
        self.execute(sql, (task_id,))
        self.commit()
