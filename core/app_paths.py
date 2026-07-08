"""Application paths module."""

import os
from pathlib import Path


def get_app_data_dir() -> Path:
    """Get the application data directory."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        base_dir = Path(local_app_data)
    else:
        base_dir = Path.home() / "AppData" / "Local"

    app_dir = base_dir / "Mreminder"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_database_path() -> Path:
    """Get the default database file path."""
    return get_app_data_dir() / "mreminder.db"
