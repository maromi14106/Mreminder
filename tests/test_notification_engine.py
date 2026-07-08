"""Tests for NotificationEngine."""

from unittest.mock import MagicMock
import pytest

from core.notification_engine import NotificationEngine
from models.task import Task
from services.task_service import TaskService
from services.notification_sound_service import NotificationSoundService


@pytest.fixture
def mock_task_service() -> MagicMock:
    service = MagicMock(spec=TaskService)
    return service


@pytest.fixture
def mock_sound_service() -> MagicMock:
    service = MagicMock(spec=NotificationSoundService)
    return service


@pytest.fixture
def engine(
    mock_task_service: MagicMock,
    mock_sound_service: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> NotificationEngine:
    eng = NotificationEngine(mock_task_service, mock_sound_service)

    # Mock the internal NotificationManager
    eng._manager = MagicMock()
    return eng


def test_check_tasks_no_due_tasks(
    engine: NotificationEngine,
    mock_task_service: MagicMock,
    mock_sound_service: MagicMock,
) -> None:
    """Test that no sound is played when there are no due tasks."""
    mock_task_service.get_due_tasks.return_value = []

    engine._check_tasks()

    mock_sound_service.play_notification.assert_not_called()


def test_check_tasks_tasks_due_but_none_shown(
    engine: NotificationEngine,
    mock_task_service: MagicMock,
    mock_sound_service: MagicMock,
) -> None:
    """Test that no sound is played if tasks are due but none are newly shown."""
    task = Task(
        id=1,
        title="Test",
        remind_at="10:00",
        repeat_type="一回",
        enabled=True,
        created_at="",
        updated_at="",
        last_notified_at=None,
        snoozed_until=None,
        next_run_at="",
        weekday=None,
    )
    mock_task_service.get_due_tasks.return_value = [task]

    # Simulate the manager saying the task is already showing
    engine._manager.show_task.return_value = False

    engine._check_tasks()

    mock_sound_service.play_notification.assert_not_called()


def test_check_tasks_multiple_shown_plays_once(
    engine: NotificationEngine,
    mock_task_service: MagicMock,
    mock_sound_service: MagicMock,
) -> None:
    """Test that sound is played exactly once even if multiple tasks are shown."""
    task1 = Task(
        id=1,
        title="Test 1",
        remind_at="10:00",
        repeat_type="一回",
        enabled=True,
        created_at="",
        updated_at="",
        last_notified_at=None,
        snoozed_until=None,
        next_run_at="",
        weekday=None,
    )
    task2 = Task(
        id=2,
        title="Test 2",
        remind_at="10:00",
        repeat_type="一回",
        enabled=True,
        created_at="",
        updated_at="",
        last_notified_at=None,
        snoozed_until=None,
        next_run_at="",
        weekday=None,
    )
    mock_task_service.get_due_tasks.return_value = [task1, task2]

    # Simulate both being shown for the first time
    engine._manager.show_task.return_value = True

    engine._check_tasks()

    mock_sound_service.play_notification.assert_called_once()
