"""Application settings module."""

from PySide6.QtCore import QSettings

from models.sound_settings import SoundSettings


class AppSettingsError(Exception):
    """Raised when application settings fail to save or load."""

    pass


class AppSettings:
    """Low-level wrapper for QSettings."""

    def __init__(self, settings: QSettings | None = None) -> None:
        """Initialize AppSettings.

        Args:
            settings: QSettings instance for testing. If None, creates a default one.
        """
        if settings is None:
            self._settings = QSettings()
        else:
            self._settings = settings

    def get_sound_settings(self) -> SoundSettings:
        """Get the current sound settings, falling back to defaults if not present."""
        try:
            enabled = self._settings.value(
                "notification_sound_enabled", True, type=bool
            )
            volume = self._settings.value("notification_sound_volume", 70, type=int)
            sound_path = self._settings.value("notification_sound_path", "", type=str)
        except Exception as e:
            raise AppSettingsError(f"通知音設定の型変換に失敗しました: {e}")

        if self._settings.status() != QSettings.Status.NoError:
            raise AppSettingsError("通知音設定の読み込みに失敗しました。")

        # Clamp volume to 0-100
        volume = max(0, min(100, volume))

        # If no path is saved, try to get the default path
        if not sound_path:
            from core.sound_files import get_default_sound_path

            path_obj = get_default_sound_path()
            if path_obj:
                sound_path = str(path_obj)

        return SoundSettings(
            enabled=enabled,
            sound_path=sound_path,
            volume=volume,
        )

    def save_sound_settings(self, settings: SoundSettings) -> None:
        """Save sound settings to QSettings."""
        clamped_volume = max(0, min(100, settings.volume))

        self._settings.setValue("notification_sound_enabled", settings.enabled)
        self._settings.setValue("notification_sound_path", settings.sound_path)
        self._settings.setValue("notification_sound_volume", clamped_volume)

        self._settings.sync()

        if self._settings.status() != QSettings.Status.NoError:
            raise AppSettingsError("Failed to save notification sound settings.")
