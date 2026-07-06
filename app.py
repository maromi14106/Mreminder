"""App module."""

from PySide6.QtWidgets import QApplication

from database.database import Database
from database.migrations import Migration
from database.repository import TaskRepository
from services.task_service import TaskService
from ui.main_window import MainWindow
from ui.theme import DARK_THEME


def create_app() -> QApplication:
    app = QApplication([])

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

    window.show()

    app.exec()