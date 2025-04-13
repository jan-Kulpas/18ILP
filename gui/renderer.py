from PyQt6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QBrush,
    QPainterPath,
    QShortcut,
    QKeySequence,
)
from PyQt6.QtCore import Qt, QPointF

from core.tile import *
from core.game import *
from core.hex import Hex

TILE_COLORS = {
    Color.BLANK: QColor("#E6E6E6"),
    Color.YELLOW: QColor("#FDE430"),
    Color.GREEN: QColor("#61B47A"),
    Color.BROWN: QColor("#BC8159"),
    Color.GRAY: QColor("#A9AFB2"),
    Color.RED: QColor("#E6262D"),
}


def lerp(a: QPointF, b: QPointF, t: float) -> QPointF:
    return a + (b - a) * t


class Renderer:
    painter: QPainter

    def __init__(self, painter: QPainter) -> None:
        self.painter = painter

    def draw_tile(self, hex: Hex, tile: Tile) -> None:
        self._draw_hex(hex, TILE_COLORS[tile.color])

        self._draw_track_group(hex, tile.tracks)

    def _draw_hex(self, hex: Hex, color: QColor) -> None:
        brush = QBrush(color)
        self.painter.setBrush(brush)
        self.painter.setPen(QPen(Qt.GlobalColor.black, 2))
        self.painter.drawPolygon(*hex.corners)
        self.painter.drawText(hex.center, str(hex))

        # #? remove later
        # painter.drawText(hex.corners[0], str(0))
        # painter.drawText(hex.midpoints[0], str(0))

    def _draw_track_group(self, hex: Hex, group: list[Track]) -> None:
        track_pens = [
            QPen(QColor("#FFFFFF"), 8),
            QPen(QColor("#000000"), 4),
        ]
        paths = [self._calculate_path(hex, track) for track in group]

        for pen in track_pens:
            for path in paths:
                self.painter.setPen(pen)
                self.painter.drawPath(path)

    def _calculate_path(self, hex: Hex, track: Track) -> QPainterPath:
        e1, e2 = track

        # Set endpoint position based on whether it goes to hex edge or a city
        p1 = hex.midpoints[e1.value] if e1.value <= 5 else hex.center
        p2 = hex.midpoints[e2.value] if e2.value <= 5 else hex.center
        middle = lerp(p1, p2, 0.5)

        # Pull control point towards center to make it actually curvy
        # 0 for straight line, 2 for alomest center
        ctrl = lerp(middle, hex.center, 0.75)

        path = QPainterPath()
        path.moveTo(p1)
        path.quadTo(ctrl, p2)

        return path
