from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QWidget,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListView,
    QPushButton,
)
from PyQt6.QtCore import Qt, QSize

from core.game import Game
from core.tile import Tile
from gui.logbox import Logbox
from gui.railway_selector import RailwaySelector
from gui.tile_preview import TilePreview
from gui.tile_selector import TileSelector

if TYPE_CHECKING:
    from main import Window

SIDEBAR_WIDTH = 300


class Sidebar(QWidget):
    game: Game
    app: Window

    tile_selector: TileSelector
    railway_selector: RailwaySelector
    logbox: Logbox

    def __init__(self, app: Window, game: Game) -> None:
        super().__init__()
        self.app = app
        self.game = game

        self.tile_selector = TileSelector(app, game)
        self.railway_selector = RailwaySelector(app, game)
        self.logbox = Logbox()

        self.setFixedWidth(SIDEBAR_WIDTH)

        layout = QVBoxLayout()
        layout.setContentsMargins(9, 0, 9, 0)
        self.setLayout(layout)

        layout.addWidget(self.tile_selector, stretch=3)
        layout.addWidget(self.railway_selector, stretch=1)
        layout.addWidget(self.logbox, stretch=1)