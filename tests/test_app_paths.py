from unittest.mock import patch

from core.app_paths import get_app_data_dir, get_database_path


def test_get_app_data_dir_with_localappdata(monkeypatch, tmp_path):
    """Test get_app_data_dir when LOCALAPPDATA is set."""
    test_dir = str(tmp_path / "AppData" / "Local")
    monkeypatch.setenv("LOCALAPPDATA", test_dir)

    app_dir = get_app_data_dir()

    assert str(app_dir).startswith(test_dir)
    assert app_dir.name == "Mreminder"


@patch("pathlib.Path.home")
@patch("pathlib.Path.mkdir")
def test_get_app_data_dir_fallback(mock_mkdir, mock_home, monkeypatch, tmp_path):
    """Test get_app_data_dir when LOCALAPPDATA is not set."""
    monkeypatch.delenv("LOCALAPPDATA", raising=False)

    # Mock home to avoid writing to real user's home directory
    mock_home.return_value = tmp_path / "fake_home"

    app_dir = get_app_data_dir()

    expected_base = mock_home.return_value / "AppData" / "Local"
    assert app_dir.parent == expected_base
    assert app_dir.name == "Mreminder"

    # Ensure it tries to create the directory
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


@patch("core.app_paths.get_app_data_dir")
def test_get_database_path(mock_get_app_data_dir, tmp_path):
    """Test get_database_path returns correct file path."""
    mock_get_app_data_dir.return_value = tmp_path / "MockAppData"
    db_path = get_database_path()

    assert db_path.name == "mreminder.db"
    assert db_path.parent == mock_get_app_data_dir.return_value
