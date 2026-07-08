"""Notification sound service module."""

from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QSoundEffect

from core.app_settings import AppSettings
from core.sound_files import (
    get_default_sound_path,
    get_windows_media_wav_files,
    is_valid_wav_path,
)
from models.sound_settings import SoundSettings


class NotificationSoundService(QObject):
    """Service to handle notification sound playback and settings."""

    def __init__(
        self,
        app_settings: AppSettings,
        sound_effect_factory: Callable[[], QSoundEffect] | None = None,
        parent: QObject | None = None,
    ) -> None:
        """Initialize the NotificationSoundService.

        Args:
            app_settings: Low-level wrapper for saving/loading settings.
            sound_effect_factory: Optional factory for creating QSoundEffect (for testing).
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._app_settings = app_settings

        if sound_effect_factory:
            self._sound_effect = sound_effect_factory()
        else:
            self._sound_effect = QSoundEffect()

        self._sound_effect.setLoopCount(1)

    def get_settings(self) -> SoundSettings:
        """Get the current sound settings."""
        return self._app_settings.get_sound_settings()

    def save_settings(self, settings: SoundSettings) -> None:
        """Save the sound settings."""
        self._app_settings.save_sound_settings(settings)

    def get_available_windows_sounds(self) -> list[Path]:
        """Get available WAV files from the Windows Media folder."""
        return get_windows_media_wav_files()

    def resolve_sound_path(self, sound_path: str) -> Path | None:
        """Resolve the given sound path or fallback to a default."""
        if is_valid_wav_path(sound_path):
            return Path(sound_path)

        return get_default_sound_path()

    def play_notification(self) -> bool:
        """Play the notification sound based on saved settings."""
        settings = self.get_settings()

        if not settings.enabled:
            return False

        return self.play_preview(settings.sound_path, settings.volume)

    def play_preview(self, sound_path: str, volume: int) -> bool:
        """Play a preview of a sound with a specific volume.

        Args:
            sound_path: Path to the WAV file.
            volume: Volume level (0-100).

        Returns:
            True if playback was successfully initiated, False otherwise.
        """
        self.stop()

        resolved_path = self.resolve_sound_path(sound_path)
        if not resolved_path:
            return False

        # Clamp volume to 0-100 and convert to 0.0-1.0
        clamped_volume = max(0, min(100, volume))
        float_volume = clamped_volume / 100.0

        try:
            self._sound_effect.setSource(
                QUrl.fromLocalFile(str(resolved_path.resolve()))
            )
            self._sound_effect.setVolume(float_volume)
            self._sound_effect.play()
            return True
        except Exception:
            return False

    def stop(self) -> None:
        """Stop any currently playing sound."""
        try:
            if self._sound_effect.isPlaying():
                self._sound_effect.stop()
        except Exception:
            pass
