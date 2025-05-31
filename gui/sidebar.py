from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QWidget,
    QTabWidget,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt, QSize

from core.game import Game
from core.tile import Tile
from gui.logbox import Logbox
from gui.railway_selector import RailwaySelector
from gui.tile_preview import TilePreview
from gui.tile_selector import TileSelector
from gui.train_selector import TrainSelector

if TYPE_CHECKING:
    from main import Window

SIDEBAR_WIDTH = 300


class Sidebar(QWidget):
    # tile_selector: TileSelector
    # railway_selector: RailwaySelector
    # logbox: Logbox

    def __init__(
        self, ts: TileSelector, ts2: TrainSelector, rs: RailwaySelector, lb: Logbox
    ) -> None:
        super().__init__()

        self.setFixedWidth(SIDEBAR_WIDTH)

        self.column = QVBoxLayout()
        self.column.setContentsMargins(9, 0, 9, 0)
        self.setLayout(self.column)

        tabs = QTabWidget()
        tabs.addTab(ts, "Tiles")
        tabs.addTab(ts2, "Trains")

        self.column.addWidget(tabs, stretch=3)
        self.column.addWidget(rs, stretch=1)
        self.column.addWidget(lb, stretch=1)
