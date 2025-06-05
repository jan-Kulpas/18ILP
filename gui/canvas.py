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
from solver.graph import Solution

if TYPE_CHECKING:
    from main import Window


class Canvas(QWidget):
    app: Window
    _solution: Solution | None

    def __init__(self, app: Window):
        super().__init__()

        self.app = app

        self._solution = None

    @property
    def solution(self) -> Solution | None:
        return self._solution

    @solution.setter
    def solution(self, new) -> None:
        self._solution = new
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # Background
        painter.fillRect(self.rect(), QColor("#f8f9fa"))
        painter.end()

        renderer = Renderer(self.app.game.year, self)

        # Draw the entire board
        for hex, tile in self.app.game.board.items():
            renderer.draw_tile(hex, tile)

        # Draw results
        # TODO: Pass train info to maybe do a legend on the side so we know which train is which.
        if self.solution:
            for train in range(len(self.solution.nodes)):
                renderer.draw_route(
                    self.solution.nodes[train], self.solution.edges[train]
                )

        # Draw selected hex
        if self.app.selected_hex:
            renderer.draw_outline(self.app.selected_hex)

    def mousePressEvent(self, event):
        pos: QPoint = event.pos()
        hex = Hex.from_pixel(pos)
        if hex in self.app.game.board:
            self.app.selected_hex = hex
        else:
            self.app.selected_hex = None
