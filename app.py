"""App module."""

import argparse
import sys
import traceback
from pathlib import Path


def run() -> None:
    # 1. コマンドライン引数のパース
    parser = argparse.ArgumentParser(description="Mreminder application")
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Start the application silently (in system tray)",
    )
    args = parser.parse_args()

    # 2. ログ初期化を最初に行う
    from core.logger import setup_logger

    logger = setup_logger()
    logger.info("Bootstrap entered before PySide6 import")

    try:
        from datetime import datetime

        # 3. GUIアプリケーションの作成
        from PySide6.QtWidgets import QApplication, QMessageBox
        from ui.theme import DARK_THEME

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        from core.version import APP_NAME, APP_VERSION

        app.setOrganizationName(APP_NAME)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        app.setQuitOnLastWindowClosed(False)
        app.setStyleSheet(DARK_THEME)

        # 起動情報の記録
        from core.app_paths import get_app_data_dir, get_database_path

        cwd = Path.cwd()
        app_data_path = get_app_data_dir()
        db_path = get_database_path()

        logger.info(f"--- {APP_NAME} Starting ---")
        logger.info(f"App Name: {APP_NAME}")
        logger.info(f"Version: {APP_VERSION}")
        logger.info(f"Date: {datetime.now().isoformat()}")
        logger.info(f"sys.executable: {sys.executable}")
        logger.info(f"sys.frozen: {getattr(sys, 'frozen', False)}")
        logger.info(f"cwd: {cwd}")
        logger.info(f"app_data_path: {app_data_path}")
        logger.info(f"database_path: {db_path}")
        logger.info(f"Mode: {'Silent' if args.silent else 'Normal'}")

        _run_app(app, args.silent, logger)
    except Exception as e:
        logger.error(f"Application crashed: {e}")
        logger.error(traceback.format_exc())
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox

            if QApplication.instance() is None:
                _app = QApplication(sys.argv)
            QMessageBox.critical(
                None, "Application Error", f"起動中にエラーが発生しました:\n\n{str(e)}"
            )
        except Exception as ui_e:
            logger.error(f"Failed to show error dialog: {ui_e}")
        sys.exit(1)


def _run_app(app, silent_mode: bool, logger) -> None:
    from core.single_instance import SingleInstance, SingleInstanceError
    from database.database import Database
    from database.migrations import Migration
    from database.repository import TaskRepository
    from database.legacy_migration import (
        migrate_legacy_database,
        LegacyDatabaseMigrationError,
    )
    from core.autostart import AutoStartRegistry
    from services.autostart_service import AutoStartService
    from services.task_service import TaskService
    from core.app_settings import AppSettings
    from services.notification_sound_service import NotificationSoundService
    from ui.main_window import MainWindow
    from core.notification_engine import NotificationEngine
    from ui.tray.tray_controller import TrayController
    from PySide6.QtWidgets import QMessageBox

    try:
        single_instance = SingleInstance()
    except SingleInstanceError as e:
        logger.error(f"SingleInstanceError during initialization: {e}")
        QMessageBox.critical(None, "起動エラー", str(e))
        return

    if not single_instance.is_primary:
        logger.info("Secondary instance detected. Notifying primary and exiting.")
        try:
            single_instance.notify_primary(silent=silent_mode)
        except SingleInstanceError as e:
            logger.error(f"Failed to notify primary instance: {e}")
            QMessageBox.critical(None, "起動エラー", str(e))
        finally:
            single_instance.close()
        return

    logger.info("Primary instance confirmed. Initializing resources...")

    if getattr(sys, "frozen", False):
        legacy_db_path = Path(sys.executable).parent / "data" / "mreminder.db"
    else:
        legacy_db_path = Path(__file__).resolve().parent / "data" / "mreminder.db"

    from core.app_paths import get_database_path

    new_db_path = get_database_path()
    try:
        if migrate_legacy_database(legacy_db_path, new_db_path):
            logger.info(f"Legacy database migrated to {new_db_path}")
    except LegacyDatabaseMigrationError as e:
        logger.error(f"Legacy database migration failed: {e}")
        QMessageBox.critical(None, "Database Migration Error", str(e))
        single_instance.close()
        return

    logger.info("Initializing database...")
    db = Database()
    Migration(db).run()
    repository = TaskRepository(db)
    task_service = TaskService(repository)

    logger.info("Initializing services...")
    autostart_registry = AutoStartRegistry()
    autostart_service = AutoStartService(autostart_registry)

    app_settings = AppSettings()
    sound_service = NotificationSoundService(app_settings)

    logger.info("Initializing UI...")
    window = MainWindow(task_service, autostart_service, sound_service)
    single_instance.show_requested.connect(window.show_window)

    engine = NotificationEngine(task_service, sound_service)
    engine.start()

    tray_controller = TrayController()
    tray_controller.show_requested.connect(window.show_window)

    def on_quick_add(minutes: int) -> None:
        task_service.quick_add(minutes)
        window.refresh_tasks()

    tray_controller.quick_add_requested.connect(on_quick_add)

    def on_quit() -> None:
        logger.info("Application quitting...")
        sound_service.stop()
        window.allow_close()
        db.close()
        single_instance.close()
        app.quit()

    tray_controller.quit_requested.connect(on_quit)

    if not silent_mode:
        window.show()

    logger.info("Entering event loop.")
    try:
        app.exec()
    finally:
        # 異常終了時もリソースを閉じるためのセーフティネット
        logger.info("Cleaning up resources...")
        try:
            sound_service.stop()
        except Exception:
            pass
        try:
            db.close()
        except Exception:
            pass
        try:
            single_instance.close()
        except Exception:
            pass
