"""Tray controller module."""

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon


class TrayController(QObject):
    """Controller for system tray icon."""

    show_requested = Signal()
    quit_requested = Signal()
    quick_add_requested = Signal(int)

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize the tray controller."""
        super().__init__(parent)
        self._tray_icon = QSystemTrayIcon(self)

        # Set temporary icon
        app = QApplication.instance()
        icon: QIcon
        if app is not None:
            # Type ignore since instance might be QCoreApplication and we assume QApplication
            icon = app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)  # type: ignore
        else:
            icon = QIcon()
        self._tray_icon.setIcon(icon)

        self._menu = QMenu()
        self._build_menu()
        self._tray_icon.setContextMenu(self._menu)
        self._tray_icon.show()
        self._tray_icon.activated.connect(self._on_activated)

    def _build_menu(self) -> None:
        """Build the tray menu."""
        action_show = QAction("開く", self)
        action_show.triggered.connect(self.show_requested.emit)
        self._menu.addAction(action_show)

        action_add_15 = QAction("クイック追加：15分後", self)
        action_add_15.triggered.connect(lambda: self.quick_add_requested.emit(15))
        self._menu.addAction(action_add_15)

        action_add_30 = QAction("クイック追加：30分後", self)
        action_add_30.triggered.connect(lambda: self.quick_add_requested.emit(30))
        self._menu.addAction(action_add_30)

        action_add_60 = QAction("クイック追加：1時間後", self)
        action_add_60.triggered.connect(lambda: self.quick_add_requested.emit(60))
        self._menu.addAction(action_add_60)

        self._menu.addSeparator()

        action_quit = QAction("終了", self)
        action_quit.triggered.connect(self.quit_requested.emit)
        self._menu.addAction(action_quit)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon activation (e.g. double click)."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_requested.emit()
