from PyQt6.QtWidgets import (
    QTextEdit
)

class Logbox(QTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)