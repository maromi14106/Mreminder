"""Settings dialog module."""

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from core.autostart import AutoStartError
from services.autostart_service import AutoStartService


class SettingsDialog(QDialog):
    """Dialog for application settings."""

    def __init__(self, parent: QWidget | None, autostart_service: AutoStartService) -> None:
        """Initialize the settings dialog."""
        super().__init__(parent)
        self.setWindowTitle("設定")
        self._autostart_service = autostart_service

        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        """Build the dialog UI."""
        layout = QVBoxLayout()

        self._autostart_checkbox = QCheckBox("Windowsログオン時に起動する")
        layout.addWidget(self._autostart_checkbox)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accepted)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def _load_settings(self) -> None:
        """Load current settings."""
        try:
            enabled = self._autostart_service.is_enabled()
            self._autostart_checkbox.setChecked(enabled)
        except AutoStartError as e:
            QMessageBox.critical(self, "エラー", f"設定の読み込みに失敗しました:\n{e}")

    def _on_accepted(self) -> None:
        """Handle OK button click."""
        enabled = self._autostart_checkbox.isChecked()
        try:
            self._autostart_service.set_enabled(enabled)
            self.accept()
        except AutoStartError as e:
            QMessageBox.critical(self, "エラー", f"設定の保存に失敗しました:\n{e}")
