from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QImage
from PyQt6.QtCore import Qt, QPoint, QPointF, QSize

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


# TODO: Add support for drawing only a hex bounding box
# TODO: Add bounding box calculation to Hex.
class BufferedPainter:
    def __init__(
        self,
        main_painter: QPainter,
        size: QSize,
        position: QPoint = QPoint(0, 0),
    ):
        self.main_painter = main_painter
        self.size = size
        self.position = position
        self.img = QImage(size, QImage.Format.Format_ARGB32_Premultiplied)
        self.img.fill(Qt.GlobalColor.transparent)

    def __enter__(self):
        self.painter = QPainter(self.img)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        return self.painter

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.painter.end()
        self.main_painter.drawImage(self.position, self.img)


class Renderer:
    painter: QPainter
    size: QSize

    def __init__(self, painter: QPainter, size: QSize) -> None:
        self.painter = painter
        self.size = size

    def draw_tile(self, hex: Hex, tile: Tile) -> None:
        self._draw_hex(hex, TILE_COLORS[tile.color])

        # TODO: Split it into tile groups based on city they are going to
        self._draw_track_group(hex, tile.tracks)

    def _draw_hex(self, hex: Hex, color: QColor) -> None:
        brush = QBrush(color)
        self.painter.setBrush(brush)
        self.painter.setPen(QPen(Qt.GlobalColor.black, 2))
        self.painter.drawPolygon(*hex.corners)
        self.painter.drawText(hex.center, str(hex))

    def _draw_track_group(self, hex: Hex, group: list[Track]) -> None:
        track_pens = [
            QPen(QColor("#FFFFFF"), 8),
            QPen(QColor("#000000"), 4),
        ]
        paths = [self._calculate_path(hex, track) for track in group]

        with BufferedPainter(self.painter, self.size) as buffer:
            for pen in track_pens:
                for path in paths:
                    buffer.setPen(pen)
                    buffer.drawPath(path)

    def _calculate_path(self, hex: Hex, track: Track) -> QPainterPath:
        e1, e2 = track

        p1 = hex.track_exit(e1)
        p2 = hex.track_exit(e2)
        middle = lerp(p1, p2, 0.5)

        # Pull control point towards center to make it actually curvy
        # 0 for straight line, 2 for alomest center
        ctrl = lerp(middle, hex.center, 0.75)

        path = QPainterPath()
        path.moveTo(p1)
        path.quadTo(ctrl, p2)

        return path
