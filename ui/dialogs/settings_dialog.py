"""Settings dialog module."""

import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from core.app_settings import AppSettingsError
from core.autostart import AutoStartError
from models.sound_settings import SoundSettings
from services.autostart_service import AutoStartService
from services.notification_sound_service import NotificationSoundService


class SettingsDialog(QDialog):
    """Dialog for application settings."""

    def __init__(
        self,
        parent: QWidget | None,
        autostart_service: AutoStartService,
        sound_service: NotificationSoundService,
    ) -> None:
        """Initialize the settings dialog."""
        super().__init__(parent)
        self.setWindowTitle("設定")
        self._autostart_service = autostart_service
        self._sound_service = sound_service

        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        """Build the dialog UI."""
        layout = QVBoxLayout()

        # Autostart Group
        autostart_group = QGroupBox("起動設定")
        autostart_layout = QVBoxLayout()
        self._autostart_checkbox = QCheckBox("Windowsログオン時に起動する")
        autostart_layout.addWidget(self._autostart_checkbox)
        autostart_group.setLayout(autostart_layout)
        layout.addWidget(autostart_group)

        # Sound Group
        sound_group = QGroupBox("通知音設定")
        sound_layout = QFormLayout()

        self._sound_enabled_check = QCheckBox("通知音を鳴らす")
        self._sound_enabled_check.toggled.connect(self._on_sound_enabled_changed)
        sound_layout.addRow(self._sound_enabled_check)

        # Path selection
        path_layout = QHBoxLayout()
        self._sound_combo = QComboBox()
        self._sound_combo.currentIndexChanged.connect(self._on_combo_changed)
        path_layout.addWidget(self._sound_combo, stretch=1)

        self._browse_button = QPushButton("参照...")
        self._browse_button.clicked.connect(self._on_browse_clicked)
        path_layout.addWidget(self._browse_button)
        sound_layout.addRow("通知音:", path_layout)

        # Volume selection
        volume_layout = QHBoxLayout()
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_layout.addWidget(self._volume_slider)

        self._volume_label = QLabel("70%")
        volume_layout.addWidget(self._volume_label)
        sound_layout.addRow("音量:", volume_layout)

        # Test play
        self._test_button = QPushButton("テスト再生")
        self._test_button.clicked.connect(self._on_test_clicked)
        sound_layout.addRow("", self._test_button)

        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.accepted.connect(self._on_accepted)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

        self.setLayout(layout)

    def _load_settings(self) -> None:
        """Load current settings."""
        has_error = False
        error_msgs = []

        try:
            enabled = self._autostart_service.is_enabled()
            self._autostart_checkbox.setChecked(enabled)
        except AutoStartError as e:
            has_error = True
            error_msgs.append(f"自動起動設定: {e}")

        try:
            sound_settings = self._sound_service.get_settings()

            # Populate combobox
            available_sounds = self._sound_service.get_available_windows_sounds()

            # Resolve the saved sound path (fallback to default if invalid/missing)
            saved_path_str = sound_settings.sound_path
            resolved_path = self._sound_service.resolve_sound_path(saved_path_str)

            added_paths: set[str] = set()
            for p in available_sounds:
                norm = os.path.normcase(str(p.resolve()))
                if norm not in added_paths:
                    self._sound_combo.addItem(p.name, str(p))
                    added_paths.add(norm)

            if (
                resolved_path
                and resolved_path.is_file()
                and resolved_path.suffix.lower() == ".wav"
            ):
                norm = os.path.normcase(str(resolved_path.resolve()))
                if norm not in added_paths:
                    self._sound_combo.addItem(resolved_path.name, str(resolved_path))
                    added_paths.add(norm)

            # Set values
            self._sound_enabled_check.setChecked(sound_settings.enabled)
            self._volume_slider.setValue(sound_settings.volume)
            self._on_volume_changed(sound_settings.volume)

            # Select the resolved path
            if resolved_path:
                norm_resolved = os.path.normcase(str(resolved_path.resolve()))
                for i in range(self._sound_combo.count()):
                    item_path_str = self._sound_combo.itemData(i)
                    if item_path_str:
                        item_path = Path(item_path_str)
                        if os.path.normcase(str(item_path.resolve())) == norm_resolved:
                            self._sound_combo.setCurrentIndex(i)
                            break

            self._on_sound_enabled_changed(sound_settings.enabled)
            self._update_test_button_state()

        except AppSettingsError as e:
            has_error = True
            error_msgs.append(f"通知音設定: {e}")

        if has_error:
            self._button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
                False
            )
            QMessageBox.critical(
                self,
                "エラー",
                "設定の読み込みに失敗しました:\n" + "\n".join(error_msgs),
            )

    def _on_sound_enabled_changed(self, enabled: bool) -> None:
        self._sound_combo.setEnabled(enabled)
        self._browse_button.setEnabled(enabled)
        self._volume_slider.setEnabled(enabled)
        self._update_test_button_state()

    def _on_combo_changed(self) -> None:
        self._update_test_button_state()

    def _update_test_button_state(self) -> None:
        enabled = self._sound_enabled_check.isChecked()
        has_items = (
            self._sound_combo.count() > 0 and self._sound_combo.itemData(0) is not None
        )

        self._test_button.setEnabled(enabled and has_items)

        if not has_items:
            self._sound_combo.clear()
            self._sound_combo.addItem("利用可能なWAVファイルがありません")
            self._sound_combo.setEnabled(False)
        else:
            if enabled:
                self._sound_combo.setEnabled(True)

    def _on_volume_changed(self, value: int) -> None:
        self._volume_label.setText(f"{value}%")

    def _on_browse_clicked(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "WAVファイルを選択", "", "WAV files (*.wav)"
        )
        if path:
            p = Path(path)
            norm_new = os.path.normcase(str(p.resolve()))

            # check if already in combo
            found_idx = -1
            for i in range(self._sound_combo.count()):
                data = self._sound_combo.itemData(i)
                if data:
                    item_path = Path(data)
                    if os.path.normcase(str(item_path.resolve())) == norm_new:
                        found_idx = i
                        break

            if found_idx >= 0:
                self._sound_combo.setCurrentIndex(found_idx)
            else:
                # Remove placeholder if it exists
                if (
                    self._sound_combo.count() == 1
                    and self._sound_combo.itemData(0) is None
                ):
                    self._sound_combo.clear()
                self._sound_combo.addItem(p.name, str(p))
                self._sound_combo.setCurrentIndex(self._sound_combo.count() - 1)

            self._update_test_button_state()

    def _on_test_clicked(self) -> None:
        current_data = self._sound_combo.currentData()
        if current_data:
            self._sound_service.play_preview(current_data, self._volume_slider.value())

    def _on_accepted(self) -> None:
        """Handle OK button click with partial success rollback."""
        new_autostart = self._autostart_checkbox.isChecked()
        current_data = self._sound_combo.currentData()
        new_sound = SoundSettings(
            enabled=self._sound_enabled_check.isChecked(),
            sound_path=current_data if current_data else "",
            volume=self._volume_slider.value(),
        )

        # Keep original to rollback if partial failure
        try:
            orig_autostart = self._autostart_service.is_enabled()
            orig_sound = self._sound_service.get_settings()
        except Exception as e:
            QMessageBox.critical(
                self, "エラー", f"元の設定の取得に失敗したため、保存を中止します:\n{e}"
            )
            return

        error_msgs = []

        # Save autostart
        autostart_saved = False
        try:
            self._autostart_service.set_enabled(new_autostart)
            autostart_saved = True
        except AutoStartError as e:
            error_msgs.append(f"自動起動設定: {e}")

        # Save sound
        sound_saved = False
        try:
            self._sound_service.save_settings(new_sound)
            sound_saved = True
        except AppSettingsError as e:
            error_msgs.append(f"通知音設定: {e}")

        # Rollback logic
        rollback_errors = []
        if error_msgs:
            if autostart_saved and not sound_saved:
                try:
                    self._autostart_service.set_enabled(orig_autostart)
                except AutoStartError as e:
                    rollback_errors.append(f"自動起動設定の復元失敗: {e}")

            if sound_saved and not autostart_saved:
                try:
                    self._sound_service.save_settings(orig_sound)
                except AppSettingsError as e:
                    rollback_errors.append(f"通知音設定の復元失敗: {e}")

        if error_msgs:
            msg = "設定の保存に失敗しました:\n" + "\n".join(error_msgs)
            if rollback_errors:
                msg += "\n\n一部の復元にも失敗しました:\n" + "\n".join(rollback_errors)
            QMessageBox.critical(self, "エラー", msg)
            return

        self.accept()

    def reject(self) -> None:
        self._sound_service.stop()
        super().reject()

    def accept(self) -> None:
        self._sound_service.stop()
        super().accept()
