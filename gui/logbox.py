from PyQt6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QLabel


class Logbox(QWidget):
    logger: QTextEdit

    def __init__(self) -> None:
        super().__init__()

        self.label = QLabel("Log:")

        self.logger = QTextEdit()
        self.logger.setReadOnly(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.logger)

        self.setLayout(layout)
