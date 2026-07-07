"""App module."""

import argparse

from PySide6.QtWidgets import QApplication

from core.autostart import AutoStartRegistry
from database.database import Database
from database.migrations import Migration
from database.repository import TaskRepository
from services.autostart_service import AutoStartService
from services.task_service import TaskService
from ui.main_window import MainWindow
from ui.theme import DARK_THEME
from ui.tray.tray_controller import TrayController


def create_app() -> QApplication:
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    app.setStyleSheet(DARK_THEME)

    return app


def run() -> None:
    parser = argparse.ArgumentParser(description="Mreminder application")
    parser.add_argument("--silent", action="store_true", help="Start the application silently (in system tray)")
    args = parser.parse_args()

    app = create_app()

    db = Database()
    Migration(db).run()
    repository = TaskRepository(db)
    task_service = TaskService(repository)
    
    autostart_registry = AutoStartRegistry()
    autostart_service = AutoStartService(autostart_registry)

    window = MainWindow(task_service, autostart_service)
    
    from core.notification_engine import NotificationEngine
    engine = NotificationEngine(task_service)
    engine.start()

    tray_controller = TrayController()

    tray_controller.show_requested.connect(window.show_window)

    def on_quick_add(minutes: int) -> None:
        task_service.quick_add(minutes)
        window.refresh_tasks()

    tray_controller.quick_add_requested.connect(on_quick_add)

    def on_quit() -> None:
        window.allow_close()
        db.close()
        app.quit()

    tray_controller.quit_requested.connect(on_quit)

    if not args.silent:
        window.show()

    app.exec()