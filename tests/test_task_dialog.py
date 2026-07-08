import sys
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTime

from ui.dialogs.task_dialog import TaskDialog
from models.task import Task
from core.schedule import truncate_to_minute


@pytest.fixture(scope="session")
def qapp():
    """Create a single QApplication instance for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_edit_expired_task_change_title_allowed(qapp, monkeypatch):
    """期限切れ一回タスクのタイトルだけの編集は可能"""
    past_dt = truncate_to_minute(datetime.now()) - timedelta(days=1)
    task = Task(
        id=1,
        title="Old Title",
        remind_at=past_dt.strftime("%H:%M"),
        repeat_type="一回",
        enabled=True,
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00",
        last_notified_at=None,
        snoozed_until=None,
        next_run_at=past_dt.isoformat(),
        weekday=None,
    )
    dialog = TaskDialog(task=task)

    dialog._title_edit.setText("New Title")

    mock_warning = MagicMock()
    monkeypatch.setattr(QMessageBox, "warning", mock_warning)

    dialog.accept()

    assert mock_warning.call_count == 0
    assert dialog.result() == 1  # Accepted


def test_edit_expired_task_change_enabled_allowed(qapp, monkeypatch):
    """期限切れ一回タスクのenabledだけの編集は可能"""
    past_dt = truncate_to_minute(datetime.now()) - timedelta(days=1)
    task = Task(
        id=1,
        title="Title",
        remind_at=past_dt.strftime("%H:%M"),
        repeat_type="一回",
        enabled=True,
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00",
        last_notified_at=None,
        snoozed_until=None,
        next_run_at=past_dt.isoformat(),
        weekday=None,
    )
    dialog = TaskDialog(task=task)

    dialog._enabled_check.setChecked(False)

    mock_warning = MagicMock()
    monkeypatch.setattr(QMessageBox, "warning", mock_warning)

    dialog.accept()

    assert mock_warning.call_count == 0
    assert dialog.result() == 1  # Accepted


def test_edit_expired_task_change_time_rejected(qapp, monkeypatch):
    """一回タスクの日時を別の過去日時へ変更すると拒否"""
    past_dt = truncate_to_minute(datetime.now()) - timedelta(days=1)
    task = Task(
        id=1,
        title="Title",
        remind_at=past_dt.strftime("%H:%M"),
        repeat_type="一回",
        enabled=True,
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00",
        last_notified_at=None,
        snoozed_until=None,
        next_run_at=past_dt.isoformat(),
        weekday=None,
    )
    dialog = TaskDialog(task=task)

    new_past_dt = past_dt - timedelta(hours=1)
    dialog._time_edit.setTime(QTime(new_past_dt.hour, new_past_dt.minute))

    mock_warning = MagicMock()
    monkeypatch.setattr(QMessageBox, "warning", mock_warning)

    dialog.accept()

    assert mock_warning.call_count == 1
    assert dialog.result() == 0  # Rejected
