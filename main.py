import sys

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QPointF
from matplotlib.backends.backend_qt import _allow_interrupt_qt

from core.tile import *
from core.game import *

from gui.renderer import Renderer
from solver.pathfinder import Pathfinder

WIDTH = 1200
HEIGHT = 800


class Window(QWidget):
    def __init__(self, game: Game, results: tuple):
        super().__init__()

        # Window settings
        self.setWindowTitle("18xx-router")
        self.setGeometry(100, 100, WIDTH, HEIGHT)  # On-screen margin and size

        # Add closing when focused on window instead of IDE
        self.shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.shortcut.activated.connect(QApplication.quit)

        self.game = game
        self.results = results

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # Background
        painter.fillRect(self.rect(), QColor("#f8f9fa"))

        renderer = Renderer(game.year, painter, self.size())

        # Draw the entire board
        for hex, tile in self.game.board.items():
            renderer.draw_tile(hex, tile)

        # Draw results
        # TODO: Pass train info to maybe do a legend on the side so we know which train is which.
        total, nodes, edges, cities = self.results

        for train in range(len(nodes)):
            nodes[train].add("E2-F1")
            renderer.draw_route(nodes[train], edges[train])

    def mousePressEvent(self, event):
        pos = event.pos()
        print(pos)


if __name__ == "__main__":
    game = Game("1889")
    game.load_save("save.json")

    pathfinder = Pathfinder(game)
    results = pathfinder.solve_for("AR")

    app = QApplication(sys.argv)
    window = Window(game, results)
    window.show()

    # hack borrowing allow_interrupt from matplotlib to unlock Ctrl+C from terminal
    with _allow_interrupt_qt(app):
        sys.exit(app.exec())
