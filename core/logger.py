"""Logger configuration module."""

import logging
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

from core.app_paths import get_app_data_dir


def setup_logger() -> logging.Logger:
    """Setup the application logger.

    Tries to use LOCALAPPDATA, falls back to TEMP if permission is denied.
    Does not raise exceptions on failure.
    """
    logger = logging.getLogger("mreminder")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.handlers:
        return logger

    try:
        app_dir = get_app_data_dir()
        log_path = app_dir / "mreminder.log"
        # Test write access
        log_path.touch(exist_ok=True)
    except OSError:
        # Fallback to temp
        try:
            app_dir = Path(tempfile.gettempdir()) / "Mreminder"
            app_dir.mkdir(parents=True, exist_ok=True)
            log_path = app_dir / "mreminder.log"
        except OSError:
            # Complete failure, just return null handler
            logger.addHandler(logging.NullHandler())
            return logger

    try:
        handler = RotatingFileHandler(
            log_path, maxBytes=1024 * 1024, backupCount=3, encoding="utf-8"
        )
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except Exception:
        logger.addHandler(logging.NullHandler())

    return logger


def get_logger() -> logging.Logger:
    """Get the application logger."""
    return logging.getLogger("mreminder")
