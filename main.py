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
from gui.logbox import Logbox
from gui.menu_bar import MenuBar
from gui.railway_selector import RailwaySelector
from gui.sidebar import SIDEBAR_WIDTH, Sidebar
from gui.tile_selector import TileSelector
from gui.train_selector import TrainSelector
from solver.pathfinder import Pathfinder

WIDTH = 1200
HEIGHT = 800


class Window(QWidget):
    game: Game
    pathfinder: Pathfinder

    ### STATE
    _selected_hex: Hex | None = None
    _selected_tile: Tile | None = None
    _selected_railway: Railway | None = None

    ### Widgets
    canvas: Canvas
    tile_selector: TileSelector
    train_selector: TrainSelector
    railway_selector: RailwaySelector
    logbox: Logbox

    @property
    def selected_railway(self) -> Railway | None:
        return self._selected_railway

    @selected_railway.setter
    def selected_railway(self, railway: Railway | None):
        self._selected_railway = railway
        self.update_routes()
        for row in self.train_selector.rows:
            row.button.setEnabled(bool(railway))
        self.tile_selector.station_button.setEnabled(
            bool(self.selected_hex and self.selected_railway)
        )
        if not self.selected_railway:
            self.railway_selector.railway_list.clearSelection()
            self.railway_selector.railway_list.clearFocus()

    @property
    def selected_hex(self) -> Hex | None:
        return self._selected_hex

    @selected_hex.setter
    def selected_hex(self, hex: Hex | None):
        self._selected_hex = hex
        self.canvas.update()
        tile = self.game.board[hex] if hex else None
        self.tile_selector.populate_tile_list(tile)
        # TODO: maybe check for if hex can have stations? try catch for now
        self.tile_selector.station_button.setEnabled(
            bool(self.selected_hex and self.selected_railway)
        )

    @property
    def selected_tile(self) -> Tile | None:
        return self._selected_tile

    @selected_tile.setter
    def selected_tile(self, tile: Tile | None):
        self._selected_tile = tile
        self.tile_selector.enable_tile_buttons(bool(tile))
        self.tile_selector.update()

    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.pathfinder = Pathfinder(game)

        self.menu = MenuBar(self)
        self.tile_selector = TileSelector(self)
        self.train_selector = TrainSelector(self)
        self.railway_selector = RailwaySelector(self)
        self.logbox = Logbox()

        # Window settings
        self.setWindowTitle("18xx-router")
        self.setGeometry(20, 40, WIDTH, HEIGHT)  # On-screen margin and size

        # Layouts
        self.canvas = Canvas(self)  # Widget for custom painting
        self.canvas.setMinimumWidth(WIDTH - SIDEBAR_WIDTH)

        self.sidebar = Sidebar(
            self.tile_selector, self.train_selector, self.railway_selector, self.logbox
        )

        layout = QHBoxLayout(self)
        layout.setMenuBar(self.menu)
        layout.addWidget(self.canvas)
        layout.addWidget(self.sidebar)
        self.setLayout(layout)

        # Add closing when focused on window instead of IDE
        self.shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.shortcut.activated.connect(QApplication.quit)

    def update_routes(self) -> None:
        if self.selected_railway:
            try:
                self.canvas.routes = self.pathfinder.solve_for(self.selected_railway.id)
            except RuleError as e:
                self.logbox.logger.append(str(e))
                self.canvas.routes = None

    def reset_state(self) -> None:
        self.selected_hex = None
        self.selected_tile = None
        self.selected_railway = None
        self.canvas.routes = None
        self.train_selector.update_train_count()
        self.logbox.logger.clear()
        self.update()


if __name__ == "__main__":
    game = Game("1889")
    game.load("save.json")

    app = QApplication(sys.argv)
    window = Window(game)
    window.show()

    # hack borrowing allow_interrupt from matplotlib to unlock Ctrl+C from terminal
    with _allow_interrupt_qt(app):
        sys.exit(app.exec())
