from collections import defaultdict
from itertools import zip_longest
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QImage
from PyQt6.QtCore import Qt, QPoint, QPointF, QSize

from core.tile import *
from core.game import *
from core.hex import Hex
from gui.helpers import lerp

TILE_COLORS = {
    Color.BLANK: QColor("#E6E6E6"),
    Color.YELLOW: QColor("#FDE430"),
    Color.GREEN: QColor("#61B47A"),
    Color.BROWN: QColor("#BC8159"),
    Color.GRAY: QColor("#A9AFB2"),
    Color.RED: QColor("#E6262D"),
}

CITY_RADIUS = 12
TOWN_RADIUS = 7


# TODO: Add support for drawing only a hex bounding box
# TODO: Add bounding box calculation to Hex.
class BufferedPainter:
    """
    A helper class that takes in a QPainter and
    returns another painter that draws to a transparent image instead.

    Upon exiting the with block, the image is automatically combined with the main painter's canvas.

    This is done to avoid an issue where the background color
    bleeds into the drawn object when painting directly
    """

    def __init__(
        self,
        main_painter: QPainter,
        size: QSize,
        position: QPoint = QPoint(0, 0),
    ) -> None:
        self.main_painter = main_painter
        self.size = size
        self.position = position
        self.img = QImage(size, QImage.Format.Format_ARGB32_Premultiplied)
        self.img.fill(Qt.GlobalColor.transparent)

    def __enter__(self) -> QPainter:
        self.painter = QPainter(self.img)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        return self.painter

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.painter.end()
        self.main_painter.drawImage(self.position, self.img)


class Renderer:
    painter: QPainter
    size: QSize

    def __init__(self, painter: QPainter, size: QSize) -> None:
        self.painter = painter
        self.size = size

    def draw_tile(self, hex: Hex, tile: Tile) -> None:
        """Draws a given Tile on the given Hex along with all its features."""
        self._draw_hex(hex, TILE_COLORS[tile.color])

        for segment in tile.segments:
            self._draw_segment(hex, segment)


        label_location = lerp(hex.center, hex.corners[-1], 0.65) - QPointF(5, 0)
        self.painter.drawText(label_location, tile.label)

    def _draw_hex(self, hex: Hex, color: QColor) -> None:
        """Draws a Tile background in the given color"""
        brush = QBrush(color)
        self.painter.setBrush(brush)
        self.painter.setPen(QPen(Qt.GlobalColor.black, 2))
        self.painter.drawPolygon(*hex.corners)

    def _draw_segment(self, hex: Hex, segment: Segment) -> None:
        track_pens = [
            #QPen(QColor("#FFFFFF"), 8),
            QPen(QColor("#000000"), 6),
        ]

        if segment.location:
            paths = [self._calculate_path(hex, track, segment.location) for track in segment.tracks]
        elif segment.tracks:
            paths = [self._calculate_path(hex, segment.tracks[0], segment.tracks[1])]
        else:
            paths = []

        with BufferedPainter(self.painter, self.size) as buffer:
            for pen in track_pens:
                for path in paths:
                    buffer.setPen(pen)
                    buffer.drawPath(path)

        if segment.settlement and segment.location:
                self._draw_settlement(hex, segment.settlement, segment.location)  

    def _calculate_path(self, hex: Hex, e1: Direction, e2: Direction | SettlementLocation) -> QPainterPath:
        """Returns a path along which a given Track should be drawn."""
        p1 = hex.midpoints[e1.value]
        match e2:
            case Direction():
                p2 = hex.midpoints[e2.value]
            case SettlementLocation():
                p2 = hex.citypoints[e2.value]
        middle = lerp(p1, p2, 0.5)

        # Pull control point towards center to make it actually curvy
        # 0 for straight line, 2 for alomest center
        ctrl = lerp(middle, hex.center, 0.75)

        path = QPainterPath()
        path.moveTo(p1)
        path.quadTo(ctrl, p2)

        return path

    def _draw_settlement(self, hex: Hex, settlement: Settlement, location: SettlementLocation) -> None:
        """Draws a city or a town on the hex."""
        center = hex.citypoints[location.value]

        if isinstance(settlement, Town):
            self.painter.setBrush(QBrush(Qt.GlobalColor.black))
            self.painter.drawEllipse(center, TOWN_RADIUS, TOWN_RADIUS)
        elif isinstance(settlement, City):
            self.painter.setBrush(QBrush(Qt.GlobalColor.white))
            points = []
            if settlement.size == 1:
                points = [center]
            elif settlement.size == 2:
                points = [
                    QPointF(center.x() - CITY_RADIUS, center.y()),
                    QPointF(center.x() + CITY_RADIUS, center.y()),
                ]
            elif settlement.size == 3:
                points = [
                    QPointF(
                        center.x() - CITY_RADIUS, center.y() + CITY_RADIUS * 0.5
                    ),
                    QPointF(
                        center.x() + CITY_RADIUS, center.y() + CITY_RADIUS * 0.5
                    ),
                    QPointF(center.x(), center.y() - CITY_RADIUS * 1.2),
                ]
            else:
                raise ValueError("City has too many stations to draw than should be possible.")

            for pt in points:
                self.painter.drawEllipse(pt, CITY_RADIUS, CITY_RADIUS)

        # ? Consider doing this after rewrite to Tile.Segment
        # ! The values will overlap if there are two cities!!!
        value_location = lerp(hex.center, hex.corners[0], 0.65) - QPointF(5, 0)
        self.painter.drawText(value_location, str(settlement.value))
