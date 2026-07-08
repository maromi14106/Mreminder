from unittest.mock import MagicMock
import sys
import pytest

from PySide6.QtWidgets import QApplication
from app import run
from core.single_instance import SingleInstance


@pytest.fixture(scope="session")
def app():
    """Ensure QApplication exists."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_app_second_instance_early_return(monkeypatch, app):
    """Test that second instance returns early and does not initialize DB etc."""
    monkeypatch.setattr(sys, "argv", ["main.py"])

    # (No need to monkeypatch QApplication because app.py checks QApplication.instance())

    # Mock setup_logger
    mock_logger = MagicMock()
    monkeypatch.setattr("core.logger.setup_logger", lambda: mock_logger)

    # Mock SingleInstance to pretend it is not primary
    mock_single_instance = MagicMock(spec=SingleInstance)
    mock_single_instance.is_primary = False

    def mock_single_instance_init(*args, **kwargs):
        return mock_single_instance

    monkeypatch.setattr(
        "core.single_instance.SingleInstance", mock_single_instance_init
    )

    # Mock Database, MainWindow to track if they were instantiated
    db_mock = MagicMock()
    monkeypatch.setattr("database.database.Database", db_mock)
    main_window_mock = MagicMock()
    monkeypatch.setattr("ui.main_window.MainWindow", main_window_mock)

    # Run app logic
    run()

    # Verify SingleInstance check was performed
    mock_single_instance.notify_primary.assert_called_once_with(silent=False)

    # Verify that heavy components were NOT created
    db_mock.assert_not_called()
    main_window_mock.assert_not_called()


def test_app_second_instance_silent(monkeypatch, app):
    """Test that silent second instance sends PING."""
    monkeypatch.setattr(sys, "argv", ["main.py", "--silent"])

    # No need to monkeypatch QApplication

    mock_logger = MagicMock()
    monkeypatch.setattr("core.logger.setup_logger", lambda: mock_logger)

    mock_single_instance = MagicMock(spec=SingleInstance)
    mock_single_instance.is_primary = False

    def mock_single_instance_init(*args, **kwargs):
        return mock_single_instance

    monkeypatch.setattr(
        "core.single_instance.SingleInstance", mock_single_instance_init
    )

    run()

    # Verify silent flag was passed
    mock_single_instance.notify_primary.assert_called_once_with(silent=True)


def test_app_startup_exception_logs_and_shows_messagebox(monkeypatch, app):
    """Test that startup exception is logged and a message box is shown."""
    monkeypatch.setattr(sys, "argv", ["main.py"])
    # No need to monkeypatch QApplication

    mock_logger = MagicMock()
    monkeypatch.setattr("core.logger.setup_logger", lambda: mock_logger)

    # Mock SingleInstance to raise an unexpected Exception
    def mock_single_instance_init(*args, **kwargs):
        raise ValueError("Unexpected Initialization Error")

    monkeypatch.setattr(
        "core.single_instance.SingleInstance", mock_single_instance_init
    )

    mock_msg_box = MagicMock()
    monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.critical", mock_msg_box)

    mock_sys_exit = MagicMock()
    monkeypatch.setattr("sys.exit", mock_sys_exit)

    run()

    mock_logger.error.assert_any_call(
        "Application crashed: Unexpected Initialization Error"
    )
    mock_msg_box.assert_called_once()
    mock_sys_exit.assert_called_once_with(1)
