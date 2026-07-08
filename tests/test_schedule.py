"""Tests for schedule calculations and task logic."""

import pytest
from datetime import datetime, tzinfo
import pathlib

from core.schedule import (
    calculate_initial_next_run,
    calculate_next_run_after_completion,
)
from models.task import Task
from services.task_service import TaskService


def test_initial_next_run_daily_future() -> None:
    now = datetime(2023, 1, 1, 10, 0)
    target = datetime(2023, 1, 1, 15, 0)
    result = calculate_initial_next_run(now, target, "毎日")
    assert result == "2023-01-01T15:00:00"


def test_initial_next_run_daily_past() -> None:
    now = datetime(2023, 1, 1, 10, 0)
    target = datetime(2023, 1, 1, 8, 0)
    result = calculate_initial_next_run(now, target, "毎日")
    assert result == "2023-01-02T08:00:00"


def test_initial_next_run_weekly_same_day_future() -> None:
    now = datetime(2023, 1, 1, 10, 0)
    target = datetime(2023, 1, 1, 15, 0)
    result = calculate_initial_next_run(now, target, "毎週", weekday=6)
    assert result == "2023-01-01T15:00:00"


def test_initial_next_run_weekly_same_day_past() -> None:
    now = datetime(2023, 1, 1, 10, 0)
    target = datetime(2023, 1, 1, 8, 0)
    result = calculate_initial_next_run(now, target, "毎週", weekday=6)
    assert result == "2023-01-08T08:00:00"


def test_next_run_after_completion_multiple_days_late() -> None:
    now = datetime(2023, 1, 5, 10, 0)
    current_run = "2023-01-01T08:00:00"
    result = calculate_next_run_after_completion(now, current_run, "毎日")
    assert result == "2023-01-06T08:00:00"


def test_next_run_after_completion_multiple_weeks_late() -> None:
    now = datetime(2023, 1, 20, 10, 0)
    current_run = "2023-01-01T08:00:00"
    result = calculate_next_run_after_completion(now, current_run, "毎週")
    assert result == "2023-01-22T08:00:00"


class DummyRepo:
    def __init__(self) -> None:
        self.tasks: list[Task] = [
            Task(
                id=1,
                title="Test",
                remind_at="10:00",
                repeat_type="毎日",
                enabled=True,
                created_at="2023-01-01T00:00:00",
                updated_at="2023-01-01T00:00:00",
                last_notified_at="2023-01-01T10:00:00",
                snoozed_until=None,
                next_run_at="2023-01-01T10:00:00",
                weekday=None,
            )
        ]
        self._next_id = 2

    def find_all(self) -> list[Task]:
        return self.tasks

    def find_by_id(self, task_id: int) -> Task | None:
        for t in self.tasks:
            if t.id == task_id:
                return Task(
                    id=t.id,
                    title=t.title,
                    remind_at=t.remind_at,
                    repeat_type=t.repeat_type,
                    enabled=t.enabled,
                    created_at=t.created_at,
                    updated_at=t.updated_at,
                    last_notified_at=t.last_notified_at,
                    snoozed_until=t.snoozed_until,
                    next_run_at=t.next_run_at,
                    weekday=t.weekday,
                )
        return None

    def update(self, task: Task) -> None:
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                self.tasks[i] = task
                break

    def create(self, task: Task) -> int:
        task.id = self._next_id
        self._next_id += 1
        self.tasks.append(task)
        return task.id


def test_no_double_notification() -> None:
    repo = DummyRepo()
    service = TaskService(repo)  # type: ignore
    now = datetime(2023, 1, 1, 10, 15)

    due = service.get_due_tasks(now)
    assert len(due) == 0

    now_next_day = datetime(2023, 1, 2, 10, 15)
    due_next_day = service.get_due_tasks(now_next_day)
    assert len(due_next_day) == 0

    repo.tasks[0].next_run_at = "2023-01-02T10:00:00"
    due_updated = service.get_due_tasks(now_next_day)
    assert len(due_updated) == 1


def test_maintain_notification_state_on_title_edit() -> None:
    repo = DummyRepo()
    repo.tasks[0].next_run_at = "2023-01-01T10:15:37"
    service = TaskService(repo)  # type: ignore
    task = repo.find_by_id(1)
    assert task is not None

    task.title = "Updated Title"
    task.enabled = False
    service.save_task(task)

    updated = repo.find_by_id(1)
    assert updated is not None
    assert updated.last_notified_at == "2023-01-01T10:00:00"
    assert updated.next_run_at == "2023-01-01T10:15:37"


def test_reset_notification_state_on_time_edit() -> None:
    repo = DummyRepo()
    service = TaskService(repo)  # type: ignore
    task = repo.find_by_id(1)
    assert task is not None

    task.remind_at = "11:00"
    task.next_run_at = "2023-01-01T11:00:00"
    service.save_task(task)

    updated = repo.find_by_id(1)
    assert updated is not None
    assert updated.last_notified_at is None


def test_validation_weekly_weekday() -> None:
    repo = DummyRepo()
    service = TaskService(repo)  # type: ignore
    task = repo.find_by_id(1)
    assert task is not None

    task.repeat_type = "毎週"
    task.weekday = None
    with pytest.raises(ValueError, match="weekday must be 0-6"):
        service.save_task(task)

    task.weekday = 7
    with pytest.raises(ValueError, match="weekday must be 0-6"):
        service.save_task(task)


def test_normalization_daily_weekday() -> None:
    repo = DummyRepo()
    service = TaskService(repo)  # type: ignore
    task = repo.find_by_id(1)
    assert task is not None

    task.repeat_type = "毎日"
    task.weekday = 3
    service.save_task(task)

    updated = repo.find_by_id(1)
    assert updated is not None
    assert updated.weekday is None


def test_snooze_with_seconds() -> None:
    repo = DummyRepo()
    repo.tasks[0].last_notified_at = None
    service = TaskService(repo)  # type: ignore

    repo.tasks[0].snoozed_until = "2023-01-01T10:30:45"

    now_before = datetime(2023, 1, 1, 10, 30, 44)
    due_before = service.get_due_tasks(now_before)
    assert len(due_before) == 0

    now_after = datetime(2023, 1, 1, 10, 30, 46)
    due_after = service.get_due_tasks(now_after)
    assert len(due_after) == 1


def test_next_run_at_seconds_precision() -> None:
    repo = DummyRepo()
    repo.tasks[0].last_notified_at = None
    repo.tasks[0].next_run_at = "2023-01-01T10:15:37"
    service = TaskService(repo)  # type: ignore

    now_before = datetime(2023, 1, 1, 10, 15, 36)
    assert len(service.get_due_tasks(now_before)) == 0

    now_exact = datetime(2023, 1, 1, 10, 15, 37)
    assert len(service.get_due_tasks(now_exact)) == 1

    now_after = datetime(2023, 1, 1, 10, 15, 45)
    assert len(service.get_due_tasks(now_after)) == 1


def test_quick_add_crosses_midnight(monkeypatch: pytest.MonkeyPatch) -> None:
    repo = DummyRepo()
    service = TaskService(repo)  # type: ignore

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz: tzinfo | None = None) -> datetime:
            return cls(2023, 1, 1, 23, 50, 45, tzinfo=tz)

    monkeypatch.setattr("services.task_service.datetime", FixedDateTime)

    task_id = service.quick_add(30)
    task = repo.find_by_id(task_id)

    assert task is not None
    assert task.next_run_at == "2023-01-02T00:20:45"
    assert task.remind_at == "00:20"
    assert task.repeat_type == "一回"
    assert task.weekday is None


def test_migration_idempotent(tmp_path: pathlib.Path) -> None:
    from database.migrations import Migration
    from database.database import Database

    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    try:
        db.execute(
            "CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, remind_at TEXT NOT NULL, repeat_type TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, last_notified_at TEXT, snoozed_until TEXT)"
        )
        db.execute(
            "INSERT INTO tasks (title, remind_at, repeat_type, created_at, updated_at) VALUES ('T1', '10:00', '毎日', '2023', '2023')"
        )
        db.commit()

        migrator = Migration(db)
        migrator.add_notification_columns()

        cursor = db.execute("SELECT next_run_at FROM tasks WHERE id = 1")
        first_run = cursor.fetchone()["next_run_at"]
        assert first_run is not None and first_run != ""

        db.execute("UPDATE tasks SET next_run_at = '2099-01-01T10:00:00' WHERE id = 1")
        db.commit()

        migrator.add_notification_columns()

        cursor = db.execute("SELECT next_run_at FROM tasks WHERE id = 1")
        second_run = cursor.fetchone()["next_run_at"]
        assert second_run == "2099-01-01T10:00:00"
    finally:
        db.close()
