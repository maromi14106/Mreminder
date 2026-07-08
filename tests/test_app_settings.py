"""Tests for application settings."""

from PySide6.QtCore import QSettings
import pytest
from pathlib import Path

from core.app_settings import AppSettings, AppSettingsError
from models.sound_settings import SoundSettings


@pytest.fixture
def temp_settings(tmp_path: Path) -> QSettings:
    """Provide a QSettings instance bound to a temporary INI file."""
    ini_path = tmp_path / "test_settings.ini"
    return QSettings(str(ini_path), QSettings.Format.IniFormat)


def test_get_sound_settings_default(temp_settings: QSettings) -> None:
    """Test getting default sound settings when nothing is saved."""
    app_settings = AppSettings(temp_settings)
    settings = app_settings.get_sound_settings()

    assert settings.enabled is True
    assert settings.volume == 70
    # sound_path might be empty or fallback to default, depending on environment.
    # We just ensure it's a string.
    assert isinstance(settings.sound_path, str)


def test_save_and_get_sound_settings(temp_settings: QSettings) -> None:
    """Test saving and getting sound settings."""
    app_settings = AppSettings(temp_settings)

    new_settings = SoundSettings(enabled=False, sound_path="C:\\test.wav", volume=42)
    app_settings.save_sound_settings(new_settings)

    loaded = app_settings.get_sound_settings()

    assert loaded.enabled is False
    assert loaded.sound_path == "C:\\test.wav"
    assert loaded.volume == 42


def test_volume_clamp_on_load(temp_settings: QSettings) -> None:
    """Test volume is clamped to 0-100 when loading."""
    # Write directly to QSettings with out-of-bounds values
    temp_settings.setValue("notification_sound_volume", -10)
    app_settings = AppSettings(temp_settings)
    loaded = app_settings.get_sound_settings()
    assert loaded.volume == 0

    temp_settings.setValue("notification_sound_volume", 150)
    loaded2 = app_settings.get_sound_settings()
    assert loaded2.volume == 100


def test_save_error_raises_exception(
    monkeypatch: pytest.MonkeyPatch, temp_settings: QSettings
) -> None:
    """Test that a save error raises AppSettingsError."""
    app_settings = AppSettings(temp_settings)
    settings = SoundSettings(enabled=True, sound_path="", volume=50)

    # Mock status to return an error
    monkeypatch.setattr(temp_settings, "status", lambda: QSettings.Status.AccessError)

    with pytest.raises(
        AppSettingsError, match="Failed to save notification sound settings."
    ):
        app_settings.save_sound_settings(settings)


def test_read_access_error(
    monkeypatch: pytest.MonkeyPatch, temp_settings: QSettings
) -> None:
    """Test that QSettings read AccessError becomes AppSettingsError."""
    app_settings = AppSettings(temp_settings)
    monkeypatch.setattr(temp_settings, "status", lambda: QSettings.Status.AccessError)

    with pytest.raises(AppSettingsError, match="通知音設定の読み込みに失敗しました。"):
        app_settings.get_sound_settings()


def test_read_type_error(
    monkeypatch: pytest.MonkeyPatch, temp_settings: QSettings
) -> None:
    """Test that QSettings type conversion failure becomes AppSettingsError."""
    app_settings = AppSettings(temp_settings)

    def mock_value(*args, **kwargs):
        raise ValueError("Invalid type")

    monkeypatch.setattr(temp_settings, "value", mock_value)

    with pytest.raises(AppSettingsError, match="通知音設定の型変換に失敗しました"):
        app_settings.get_sound_settings()


def test_save_clamp_volume(temp_settings: QSettings) -> None:
    """Test that save_sound_settings clamps volume to 0-100 before saving."""
    app_settings = AppSettings(temp_settings)

    # Save volume -10
    settings_under = SoundSettings(enabled=True, sound_path="", volume=-10)
    app_settings.save_sound_settings(settings_under)
    assert temp_settings.value("notification_sound_volume", type=int) == 0

    # Save volume 150
    settings_over = SoundSettings(enabled=True, sound_path="", volume=150)
    app_settings.save_sound_settings(settings_over)
    assert temp_settings.value("notification_sound_volume", type=int) == 100
