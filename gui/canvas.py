from __future__ import annotations

from typing import TYPE_CHECKING, Any
from PyQt6.QtWidgets import (
    QWidget,
)
from PyQt6.QtGui import (
    QPainter,
    QColor,
)
from PyQt6.QtCore import QPoint

from core.game import Game
from core.hex import Hex
from gui.renderer import Renderer

if TYPE_CHECKING:
    from main import Window


class Canvas(QWidget):
    app: Window
    game: Game
    _routes: Any

    def __init__(self, app: Window, game: Game):
        super().__init__()

        self.app = app

        self.game = game
        self._routes = None

    @property
    def routes(self) -> Any:
        return self._routes

    @routes.setter
    def routes(self, new) -> None:
        self._routes = new
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # Background
        painter.fillRect(self.rect(), QColor("#f8f9fa"))
        painter.end()

        renderer = Renderer(self.game.year, self)

        # Draw the entire board
        for hex, tile in self.game.board.items():
            renderer.draw_tile(hex, tile)

        # Draw results
        # TODO: Pass train info to maybe do a legend on the side so we know which train is which.
        if self.routes:
            total, nodes, edges, cities = self.routes
            for train in range(len(nodes)):
                renderer.draw_route(nodes[train], edges[train])

        # Draw selected hex
        if self.app.selected_hex:
            renderer.draw_outline(self.app.selected_hex)

    def mousePressEvent(self, event):
        pos: QPoint = event.pos()
        hex = Hex.from_pixel(pos)
        if hex in self.game.board:
            tile = self.game.board[hex]
            self.app.selected_hex = hex
            self.app.sidebar.tile_selector.populate_tile_list(tile)
            self.update()
        else:
            self.app.sidebar.tile_selector.reset_tile_list()
            self.app.selected_hex = None
