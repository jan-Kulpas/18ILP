from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QShortcut, QKeySequence
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
    Color.RED: QColor("#E6262D")
}

class Renderer:
    @staticmethod
    def draw_tile(painter: QPainter, hex: Hex, tile: Tile) -> None:
        def lerp(a: QPointF, b: QPointF, t: float) -> QPointF:
            return a + (b - a) * t


        brush = QBrush(TILE_COLORS[tile.color])
        painter.setBrush(brush)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawPolygon(*hex.corners)

        painter.drawText(hex.center, str(hex))

        # #? remove later
        # painter.drawText(hex.corners[0], str(0))
        # painter.drawText(hex.midpoints[0], str(0))

        #Draw tracks
        track_pens = [QPen(QColor("#FFFFFF"), 8), QPen(QColor("#000000"), 4)]
        for start_edge, end_edge in tile.tracks:
            # Set endpoint position based on whether it goes to hex edge or a city
            p1 = hex.midpoints[start_edge.value] if start_edge.value <= 5 else hex.center
            p2 = hex.midpoints[end_edge.value] if end_edge.value <= 5 else hex.center
            middle = lerp(p1, p2, 0.5)

            # Pull control point towards center to make it actually curvy 
            ctrl = lerp(middle, hex.center, 0.75) # 0 for straight line, 2 for alomest center

            path = QPainterPath()
            path.moveTo(p1)
            path.quadTo(ctrl, p2)
            for pen in track_pens:
                painter.setPen(pen)
                painter.drawPath(path)
