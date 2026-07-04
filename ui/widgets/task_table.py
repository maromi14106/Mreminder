"""Task table widget module."""

from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget


class TaskTable(QTableWidget):
    """Table widget for displaying tasks."""

    def __init__(self) -> None:
        """Initialize the task table."""
        super().__init__()

        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(
            ["✔", "タイトル", "時刻", "繰り返し", "状態"]
        )

        # 行単位での選択、単一行のみ選択可
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # 編集禁止
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # 列幅とヘッダーの設定
        header = self.horizontalHeader()
        
        # ✔列: 固定幅
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(0, 30)
        
        # タイトル列: 残りのスペースを埋める
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # 時刻列: 固定幅
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(2, 100)
        
        # 繰り返し列: 固定幅
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(3, 100)
        
        # 状態列: 固定幅
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(4, 80)
