"""Tests for sound files module."""

import os
from pathlib import Path

import pytest

from core.sound_files import (
    get_default_sound_path,
    get_windows_media_wav_files,
    is_valid_wav_path,
)


def setup_mock_media_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Setup a mock Windows directory with a Media folder."""
    windir = tmp_path / "Windows"
    media_dir = windir / "Media"
    media_dir.mkdir(parents=True)

    # Create some dummy files
    (media_dir / "windows notify system generic.wav").write_text("dummy")
    (media_dir / "System_Notify.WAV").write_text("dummy")  # Uppercase extension
    (media_dir / "other.wav").write_text("dummy")
    (media_dir / "not_a_sound.txt").write_text("dummy")

    # Subdirectory
    sub_dir = media_dir / "SubDir"
    sub_dir.mkdir()
    (sub_dir / "sub_sound.wav").write_text("dummy")

    # Directory named .wav (should not be included)
    (media_dir / "fake_dir.wav").mkdir()

    monkeypatch.setenv("WINDIR", str(windir))
    return media_dir


def test_get_windows_media_wav_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test getting WAV files from the media directory."""
    setup_mock_media_dir(tmp_path, monkeypatch)

    files = get_windows_media_wav_files()

    # Should find 4 valid wav files (generic, notify, other, sub_sound)
    assert len(files) == 4

    # Check that the directory named .wav is NOT included
    for f in files:
        assert f.is_file()
        assert f.suffix.lower() == ".wav"

    # Check that they are sorted
    paths_str = [os.path.normcase(str(p)) for p in files]
    assert paths_str == sorted(paths_str)


def test_get_default_sound_path_generic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test getting default sound prioritizes 'windows notify system generic.wav'."""
    setup_mock_media_dir(tmp_path, monkeypatch)

    default = get_default_sound_path()
    assert default is not None
    assert default.name.lower() == "windows notify system generic.wav"


def test_get_default_sound_path_notify(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test getting default sound falls back to a file with 'notify' in the name."""
    windir = tmp_path / "Windows"
    media_dir = windir / "Media"
    media_dir.mkdir(parents=True)
    (media_dir / "my_notify_sound.wav").write_text("dummy")
    (media_dir / "z_other.wav").write_text("dummy")
    monkeypatch.setenv("WINDIR", str(windir))

    default = get_default_sound_path()
    assert default is not None
    assert default.name == "my_notify_sound.wav"


def test_get_default_sound_path_first(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test getting default sound falls back to the first sorted file."""
    windir = tmp_path / "Windows"
    media_dir = windir / "Media"
    media_dir.mkdir(parents=True)
    (media_dir / "b_sound.wav").write_text("dummy")
    (media_dir / "a_sound.wav").write_text("dummy")
    monkeypatch.setenv("WINDIR", str(windir))

    default = get_default_sound_path()
    assert default is not None
    # a_sound.wav should be first when sorted
    assert default.name == "a_sound.wav"


def test_get_default_sound_path_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test getting default sound returns None if no WAV files exist."""
    windir = tmp_path / "Windows"
    media_dir = windir / "Media"
    media_dir.mkdir(parents=True)
    monkeypatch.setenv("WINDIR", str(windir))

    default = get_default_sound_path()
    assert default is None


def test_is_valid_wav_path(tmp_path: Path) -> None:
    """Test path validation."""
    valid_wav = tmp_path / "test.wav"
    valid_wav.write_text("dummy")

    valid_WAV = tmp_path / "test2.WAV"
    valid_WAV.write_text("dummy")

    not_wav = tmp_path / "test.txt"
    not_wav.write_text("dummy")

    dir_wav = tmp_path / "dir.wav"
    dir_wav.mkdir()

    not_exist = tmp_path / "nonexistent.wav"

    assert is_valid_wav_path(str(valid_wav)) is True
    assert is_valid_wav_path(str(valid_WAV)) is True
    assert is_valid_wav_path(str(not_wav)) is False
    assert is_valid_wav_path(str(dir_wav)) is False
    assert is_valid_wav_path(str(not_exist)) is False
    assert is_valid_wav_path("") is False
