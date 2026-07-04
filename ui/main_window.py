"""Main window module."""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.task_table import TaskTable


class MainWindow(QMainWindow):
    """Main window of the application."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()

        self.setWindowTitle("こくまろりまいんだー Pro")
        self.resize(900, 600)

        # アクションとウィジェットのインスタンス変数を型ヒント付きで宣言
        self._action_add: QAction
        self._action_edit: QAction
        self._action_delete: QAction
        self._action_quick_add: QAction

        self._task_table: TaskTable
        self._status_task_count: QLabel
        self._status_next_notify: QLabel

        self._build_ui()

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
        # テーブルを広く使うためマージンを調整
        layout.setContentsMargins(10, 10, 10, 10)
        
        self._task_table = TaskTable()
        layout.addWidget(self._task_table)
        
        central.setLayout(layout)
        self.setCentralWidget(central)

    def _create_statusbar(self) -> None:
        """Create and set up the status bar."""
        statusbar = self.statusBar()
        
        # 左側にタスク数を表示
        self._status_task_count = QLabel("タスク数：0")
        statusbar.addWidget(self._status_task_count)
        
        # 右側に次回通知を表示 (addPermanentWidgetで右寄せになる)
        self._status_next_notify = QLabel("次回通知：なし")
        statusbar.addPermanentWidget(self._status_next_notify)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        self._action_add.triggered.connect(self._show_not_implemented)
        self._action_edit.triggered.connect(self._show_not_implemented)
        self._action_delete.triggered.connect(self._show_not_implemented)
        self._action_quick_add.triggered.connect(self._show_not_implemented)

    def _show_not_implemented(self) -> None:
        """Show a 'not implemented' message box."""
        QMessageBox.information(self, "情報", "未実装です")