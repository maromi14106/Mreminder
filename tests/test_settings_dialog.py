"""Tests for settings dialog."""

import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication, QDialogButtonBox, QMessageBox

from core.app_settings import AppSettingsError
from models.sound_settings import SoundSettings
from services.autostart_service import AutoStartService
from services.notification_sound_service import NotificationSoundService
from ui.dialogs.settings_dialog import SettingsDialog


@pytest.fixture(scope="session")
def qapp():
    """Create a single QApplication instance for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_autostart_service() -> MagicMock:
    service = MagicMock(spec=AutoStartService)
    service.is_enabled.return_value = False
    return service


@pytest.fixture
def mock_sound_service(tmp_path: Path) -> MagicMock:
    service = MagicMock(spec=NotificationSoundService)
    service.get_settings.return_value = SoundSettings(True, "", 70)

    # Create some fake available sounds
    sound1 = tmp_path / "sound1.wav"
    sound1.write_text("dummy")
    sound2 = tmp_path / "sound2.wav"
    sound2.write_text("dummy")

    service.get_available_windows_sounds.return_value = [sound1, sound2]
    service.resolve_sound_path.return_value = sound1

    return service


@pytest.fixture
def dialog(qapp, mock_autostart_service, mock_sound_service) -> SettingsDialog:
    dlg = SettingsDialog(None, mock_autostart_service, mock_sound_service)
    return dlg


def test_fallback_path_is_selected_but_not_saved_until_ok(
    qapp, mock_autostart_service, mock_sound_service, tmp_path
) -> None:
    """削除済み保存パスではresolved fallbackが設定画面で選択される。
    フォールバック表示だけでは設定は保存されない。"""

    # Create a fallback sound that resolve_sound_path will return
    fallback_sound = tmp_path / "fallback.wav"
    fallback_sound.write_text("dummy")

    # Pretend the saved settings had an invalid path, but resolve returns fallback
    mock_sound_service.get_settings.return_value = SoundSettings(
        True, "C:\\invalid.wav", 70
    )
    mock_sound_service.resolve_sound_path.return_value = fallback_sound

    dlg = SettingsDialog(None, mock_autostart_service, mock_sound_service)

    # The combo should contain the fallback sound and it should be selected
    assert dlg._sound_combo.currentText() == "fallback.wav"

    # Verify save hasn't been called just by loading
    mock_sound_service.save_settings.assert_not_called()

    # Click OK to save
    dlg._on_accepted()

    # Now save should have been called with the fallback path
    mock_sound_service.save_settings.assert_called_once()
    saved_arg = mock_sound_service.save_settings.call_args[0][0]
    assert saved_arg.sound_path == str(fallback_sound)


def test_initial_load_error_disables_ok_button(
    qapp, mock_autostart_service, mock_sound_service, monkeypatch
) -> None:
    """初期読込失敗時はOKボタンが無効"""

    mock_sound_service.get_settings.side_effect = AppSettingsError("Failed to read")

    # Prevent QMessageBox from actually showing
    monkeypatch.setattr(QMessageBox, "critical", MagicMock())

    dlg = SettingsDialog(None, mock_autostart_service, mock_sound_service)

    ok_button = dlg._button_box.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_button.isEnabled() is False


def test_fetch_original_state_failure_aborts_save(
    qapp, mock_autostart_service, mock_sound_service, monkeypatch
) -> None:
    """元設定の取得失敗時はset_enabledとsave_settingsを呼ばない"""

    dlg = SettingsDialog(None, mock_autostart_service, mock_sound_service)

    # Make get_settings fail *after* the dialog is loaded (when OK is clicked)
    mock_sound_service.get_settings.side_effect = AppSettingsError(
        "Cannot fetch original"
    )
    monkeypatch.setattr(QMessageBox, "critical", MagicMock())

    # Reset mock to clear load calls
    mock_autostart_service.set_enabled.reset_mock()
    mock_sound_service.save_settings.reset_mock()

    # Trigger accepted
    dlg._on_accepted()

    # Neither should be called because fetch failed
    mock_autostart_service.set_enabled.assert_not_called()
    mock_sound_service.save_settings.assert_not_called()


def test_cancel_does_not_save_and_calls_stop(
    qapp, mock_autostart_service, mock_sound_service
) -> None:
    """キャンセルでは保存されずstopのみ呼ばれる"""
    dlg = SettingsDialog(None, mock_autostart_service, mock_sound_service)

    # Reset mock
    mock_sound_service.save_settings.reset_mock()
    mock_sound_service.stop.reset_mock()

    dlg.reject()

    mock_sound_service.save_settings.assert_not_called()
    mock_sound_service.stop.assert_called_once()
