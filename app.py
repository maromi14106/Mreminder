"""App module."""

from PySide6.QtWidgets import QApplication

from database.database import Database
from database.migrations import Migration
from database.repository import TaskRepository
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
    app = create_app()

    db = Database()
    Migration(db).run()
    repository = TaskRepository(db)
    task_service = TaskService(repository)

    window = MainWindow(task_service)
    
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

    window.show()

    app.exec()