"""Sound settings module."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SoundSettings:
    """Settings for notification sounds."""

    enabled: bool
    sound_path: str
    volume: int
