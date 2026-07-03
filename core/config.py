from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"

SETTINGS_FILE = DATA_DIR / "settings.json"
TASKS_FILE = DATA_DIR / "tasks.json"