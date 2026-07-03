from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("こくまろりまいんだー Pro")
        self.resize(900, 600)

        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()

        layout = QVBoxLayout()

        title = QLabel("こくまろりまいんだー Pro")
        title.setStyleSheet(
            "font-size:24px;font-weight:bold;"
        )

        subtitle = QLabel(
            "v0.1.0 - Project Bootstrap"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)

        central.setLayout(layout)

        self.setCentralWidget(central)