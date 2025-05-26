from __future__ import annotations
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
)
from PyQt6.QtGui import (
    QShortcut,
    QKeySequence,
)
from PyQt6.QtCore import QPoint
from matplotlib.backends.backend_qt import _allow_interrupt_qt

from core.tile import *
from core.game import *

from gui.canvas import Canvas
from gui.sidebar import SIDEBAR_WIDTH, Sidebar
from solver.pathfinder import Pathfinder

WIDTH = 1200
HEIGHT = 800


class Window(QWidget):
    game: Game
    pathfinder: Pathfinder

    ### STATE
    selected_hex: Hex | None
    selected_tile: Tile | None
    selected_railway: Railway | None

    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.pathfinder = Pathfinder(game)

        self.selected_hex = None
        self.selected_tile = None
        self.selected_railway = None

        # Window settings
        self.setWindowTitle("18xx-router")
        self.setGeometry(20, 40, WIDTH, HEIGHT)  # On-screen margin and size

        # Layouts
        self.canvas = Canvas(self, game)  # Widget for custom painting
        self.canvas.setMinimumWidth(WIDTH - SIDEBAR_WIDTH)

        self.sidebar = Sidebar(self, game)

        layout = QHBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.addWidget(self.sidebar)
        self.setLayout(layout)

        # Add closing when focused on window instead of IDE
        self.shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.shortcut.activated.connect(QApplication.quit)

    def update_routes(self) -> None:
        if self.selected_railway:
            self.canvas.routes = self.pathfinder.solve_for(self.selected_railway.id)



if __name__ == "__main__":
    game = Game("1889")
    game.load_save("save.json")

    app = QApplication(sys.argv)
    window = Window(game)
    window.show()

    # hack borrowing allow_interrupt from matplotlib to unlock Ctrl+C from terminal
    with _allow_interrupt_qt(app):
        sys.exit(app.exec())
