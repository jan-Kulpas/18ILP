import sys

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QPointF
from matplotlib.backends.backend_qt import _allow_interrupt_qt

from core.tile import *
from core.game import *

from gui.renderer import Renderer

WIDTH = 1200
HEIGHT = 800


class Window(QWidget):
    def __init__(self, game: Game):
        super().__init__()

        # Window settings
        self.setWindowTitle("18xx-router")
        self.setGeometry(100, 100, WIDTH, HEIGHT)  # On-screen margin and size

        # Add closing when focused on window instead of IDE
        self.shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.shortcut.activated.connect(QApplication.quit)

        self.game = game

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # Background
        painter.fillRect(self.rect(), QColor("#f8f9fa"))

        renderer = Renderer(painter)

        # Draw the entire board
        for hex, field in self.game.board.items():
            renderer.draw_tile(hex, field.tile)

    def mousePressEvent(self, event):
        pos = event.pos()
        print(pos)


if __name__ == "__main__":
    game = Game("1889")

    app = QApplication(sys.argv)
    window = Window(game)
    window.show()

    # print(game.board)

    # hack borrowing allow_interrupt from matplotlib to unlock Ctrl+C from terminal
    with _allow_interrupt_qt(app):
        sys.exit(app.exec())
