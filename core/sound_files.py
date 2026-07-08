"""Sound files module for searching and resolving WAV files."""

import os
from pathlib import Path


def get_windows_media_wav_files() -> list[Path]:
    """Get a list of all WAV files in the Windows Media folder."""
    windir = os.environ.get("WINDIR", r"C:\Windows")
    media_dir = Path(windir) / "Media"

    if not media_dir.exists() or not media_dir.is_dir():
        return []

    wav_files: list[Path] = []
    seen_paths: set[str] = set()

    # Safely traverse the directory structure
    try:
        for root, _, files in os.walk(media_dir):
            for file in files:
                if file.lower().endswith(".wav"):
                    path = Path(root) / file
                    try:
                        if path.is_file():
                            norm_path = os.path.normcase(str(path.resolve()))
                            if norm_path not in seen_paths:
                                seen_paths.add(norm_path)
                                wav_files.append(path)
                    except OSError:
                        # Ignore unreadable files or broken symlinks
                        pass
    except OSError:
        # Ignore unreadable directories
        pass

    # Sort stably by case-insensitive path
    wav_files.sort(key=lambda p: os.path.normcase(str(p)))
    return wav_files


def get_default_sound_path() -> Path | None:
    """Get the default sound path from Windows Media."""
    files = get_windows_media_wav_files()
    if not files:
        return None

    # 1. Windows Notify System Generic.wav
    for file in files:
        if file.name.lower() == "windows notify system generic.wav":
            return file

    # 2. File with 'notify' in the name
    for file in files:
        if "notify" in file.name.lower():
            return file

    # 3. First file in the sorted list
    return files[0]


def is_valid_wav_path(path_str: str) -> bool:
    """Check if the given path is a valid existing WAV file."""
    if not path_str:
        return False

    try:
        path = Path(path_str)
        if path.is_file() and path.suffix.lower() == ".wav":
            return True
    except OSError:
        pass

    return False
