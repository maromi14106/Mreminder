from PySide6.QtWidgets import QApplication

from core.config import SETTINGS_FILE, TASKS_FILE
from core.storage import load_json, save_json
from ui.main_window import MainWindow
from ui.theme import DARK_THEME


DEFAULT_SETTINGS = {
    "theme": "dark",
    "start_with_windows": False,
    "notification_position": "bottom_right",
}


def initialize_files() -> None:
    settings = load_json(
        SETTINGS_FILE,
        DEFAULT_SETTINGS,
    )

    save_json(
        SETTINGS_FILE,
        settings,
    )

    tasks = load_json(
        TASKS_FILE,
        [],
    )

    save_json(
        TASKS_FILE,
        tasks,
    )


def create_app() -> QApplication:
    app = QApplication([])

    app.setStyleSheet(DARK_THEME)

    return app


def run() -> None:
    initialize_files()

    app = create_app()

    window = MainWindow()
    window.show()

    app.exec()