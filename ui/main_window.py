"""Main window module."""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from database.database import Database
from database.repository import TaskRepository
from services.task_service import TaskService
from ui.dialogs.task_dialog import TaskDialog
from ui.widgets.task_table import TaskTable

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
MARGIN = 10


class MainWindow(QMainWindow):
    """Main window of the application."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()

        self.setWindowTitle("Mreminder")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self._db = Database()
        self._repository = TaskRepository(self._db)
        self._task_service = TaskService(self._repository)

        self._action_add: QAction
        self._action_edit: QAction
        self._action_delete: QAction
        self._action_quick_add: QAction

        self._task_table: TaskTable
        self._status_task_count: QLabel
        self._status_next_notify: QLabel

        self._build_ui()
        self._load_tasks()

    def _build_ui(self) -> None:
        """Build the complete UI."""
        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._create_central_widget()
        self._create_statusbar()
        self._connect_signals()

    def _create_actions(self) -> None:
        """Create actions for menus and toolbars."""
        self._action_add = QAction("追加", self)
        self._action_edit = QAction("編集", self)
        self._action_delete = QAction("削除", self)
        self._action_quick_add = QAction("クイック追加", self)

    def _create_menu(self) -> None:
        """Create the menu bar."""
        menubar = self.menuBar()
        menubar.addMenu("ファイル")
        menubar.addMenu("編集")
        menubar.addMenu("設定")
        menubar.addMenu("ヘルプ")

    def _create_toolbar(self) -> None:
        """Create the main toolbar."""
        toolbar = self.addToolBar("メインツールバー")
        toolbar.setMovable(False)
        toolbar.addAction(self._action_add)
        toolbar.addAction(self._action_edit)
        toolbar.addAction(self._action_delete)
        toolbar.addSeparator()
        toolbar.addAction(self._action_quick_add)

    def _create_central_widget(self) -> None:
        """Create and set the central widget."""
        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        
        self._task_table = TaskTable()
        layout.addWidget(self._task_table)
        
        central.setLayout(layout)
        self.setCentralWidget(central)

    def _create_statusbar(self) -> None:
        """Create and set up the status bar."""
        statusbar = self.statusBar()
        
        self._status_task_count = QLabel("タスク数：0")
        statusbar.addWidget(self._status_task_count)
        
        self._status_next_notify = QLabel("次回通知：なし")
        statusbar.addPermanentWidget(self._status_next_notify)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        self._action_add.triggered.connect(self._on_action_add_triggered)
        self._action_edit.triggered.connect(self._show_not_implemented)
        self._action_delete.triggered.connect(self._show_not_implemented)
        self._action_quick_add.triggered.connect(self._show_not_implemented)

    def _on_action_add_triggered(self) -> None:
        """Handle the add action."""
        dialog = TaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task = dialog.get_task()
            
            task_id = self._task_service.add_task(task)
            task.id = task_id
            
            self._task_table.add_task(task)
            self._update_statusbar()

    def _load_tasks(self) -> None:
        """Load tasks from database and populate the table."""
        tasks = self._task_service.get_tasks()
        self._task_table.set_tasks(tasks)
        self._update_statusbar()

    def _update_statusbar(self) -> None:
        """Update the status bar information."""
        count = self._task_table.rowCount()
        self._status_task_count.setText(f"タスク数：{count}")
        self._status_next_notify.setText("次回通知：なし")

    def _show_not_implemented(self) -> None:
        """Show a 'not implemented' message box."""
        QMessageBox.information(self, "情報", "未実装です")