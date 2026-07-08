"""Tests for the notification sound service."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from core.app_settings import AppSettings
from models.sound_settings import SoundSettings
from services.notification_sound_service import NotificationSoundService


@pytest.fixture
def mock_app_settings(monkeypatch: pytest.MonkeyPatch) -> AppSettings:
    """Provide a mocked AppSettings."""
    settings = AppSettings()
    # Mock default settings
    monkeypatch.setattr(
        settings, "get_sound_settings", lambda: SoundSettings(True, "", 70)
    )
    return settings


@pytest.fixture
def mock_sound_effect() -> MagicMock:
    """Provide a mock QSoundEffect."""
    return MagicMock()


@pytest.fixture
def sound_service(
    mock_app_settings: AppSettings, mock_sound_effect: MagicMock
) -> NotificationSoundService:
    """Provide a NotificationSoundService with mocked dependencies."""
    return NotificationSoundService(
        mock_app_settings, sound_effect_factory=lambda: mock_sound_effect
    )


def test_play_preview_volume_clamping(
    sound_service: NotificationSoundService,
    mock_sound_effect: MagicMock,
    tmp_path: Path,
) -> None:
    """Test that volume is clamped and scaled correctly during preview."""
    valid_wav = tmp_path / "test.wav"
    valid_wav.write_text("dummy")

    # Test volume 150 -> clamped to 100 -> 1.0
    assert sound_service.play_preview(str(valid_wav), 150) is True
    mock_sound_effect.setVolume.assert_called_with(1.0)
    mock_sound_effect.play.assert_called()

    # Test volume -10 -> clamped to 0 -> 0.0
    assert sound_service.play_preview(str(valid_wav), -10) is True
    mock_sound_effect.setVolume.assert_called_with(0.0)


def test_play_preview_invalid_path(
    sound_service: NotificationSoundService,
    mock_sound_effect: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that an invalid path returns False and does not play."""
    monkeypatch.setattr(sound_service, "resolve_sound_path", lambda x: None)
    assert sound_service.play_preview("", 50) is False
    mock_sound_effect.play.assert_not_called()


def test_play_notification_disabled(
    sound_service: NotificationSoundService,
    mock_sound_effect: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that playing a notification returns False if disabled."""
    monkeypatch.setattr(
        sound_service._app_settings,
        "get_sound_settings",
        lambda: SoundSettings(False, "dummy.wav", 50),
    )

    assert sound_service.play_notification() is False
    mock_sound_effect.play.assert_not_called()


def test_play_notification_success(
    sound_service: NotificationSoundService,
    mock_sound_effect: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Test that playing a notification succeeds when enabled with a valid path."""
    valid_wav = tmp_path / "test.wav"
    valid_wav.write_text("dummy")

    monkeypatch.setattr(
        sound_service._app_settings,
        "get_sound_settings",
        lambda: SoundSettings(True, str(valid_wav), 50),
    )

    assert sound_service.play_notification() is True
    mock_sound_effect.play.assert_called_once()
    mock_sound_effect.setVolume.assert_called_with(0.5)


def test_stop_calls_sound_effect_stop(
    sound_service: NotificationSoundService, mock_sound_effect: MagicMock
) -> None:
    """Test that stop() calls the underlying QSoundEffect stop method if playing."""
    mock_sound_effect.isPlaying.return_value = True
    sound_service.stop()
    mock_sound_effect.stop.assert_called_once()


def test_stop_ignores_exceptions(
    sound_service: NotificationSoundService, mock_sound_effect: MagicMock
) -> None:
    """stopのisPlayingが例外を出しても外へ伝播しない"""
    # Make isPlaying raise an exception
    mock_sound_effect.isPlaying.side_effect = Exception("Backend crash")

    # Should not raise
    sound_service.stop()
    mock_sound_effect.stop.assert_not_called()
