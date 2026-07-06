"""Notification manager module."""

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QGuiApplication

from models.task import Task
from ui.notifications.notification_popup import NotificationPopup


class NotificationManager(QObject):
    """Manager for displaying and stacking notification popups."""

    popup_completed = Signal(Task)
    popup_snoozed = Signal(Task)

    def __init__(self) -> None:
        """Initialize the notification manager."""
        super().__init__()
        self._popups: list[NotificationPopup] = []
        self._margin_right = 20
        self._margin_bottom = 20
        self._spacing = 10

    def show_task(self, task: Task) -> bool:
        """
        Show a notification for the given task.
        Returns False if the task is already being shown.
        """
        for popup in self._popups:
            if popup.task.id == task.id:
                return False

        popup = NotificationPopup(task)
        popup.completed.connect(self._on_popup_completed)
        popup.snoozed.connect(self._on_popup_snoozed)
        
        self._popups.append(popup)
        self._recalculate_positions()
        
        popup.show()
        return True

    def _on_popup_completed(self, task: Task) -> None:
        """Handle popup completion."""
        self._remove_popup_for_task(task)
        self.popup_completed.emit(task)

    def _on_popup_snoozed(self, task: Task) -> None:
        """Handle popup snooze."""
        self._remove_popup_for_task(task)
        self.popup_snoozed.emit(task)

    def _remove_popup_for_task(self, task: Task) -> None:
        """Remove and close the popup for a given task."""
        for popup in self._popups:
            if popup.task.id == task.id:
                self._popups.remove(popup)
                popup.close()
                popup.deleteLater()
                break
                
        self._recalculate_positions()

    def _recalculate_positions(self) -> None:
        """Recalculate positions to stack popups in the bottom right corner."""
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
            
        geometry = screen.availableGeometry()
        
        current_bottom = geometry.bottom() - self._margin_bottom
        right = geometry.right() - self._margin_right
        
        for popup in self._popups:
            x = right - popup.width()
            y = current_bottom - popup.height()
            popup.move(x, y)
            
            current_bottom = y - self._spacing
