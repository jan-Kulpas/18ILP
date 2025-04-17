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

        groups = self._group_tracks(tile.tracks)

        # ?: maybe do this at some point
        # ?: or split tile.tracks into tile.segments with baked in towns?
        # ! This is really ugly and could be improved by making track into a class with a getCity method
        for group, city in zip_longest(groups, tile.cities):
            if group:
                self._draw_track_group(hex, group)
            if city:
                self._draw_city(hex, city, group)

        label_location = lerp(hex.center, hex.corners[-1], 0.65) - QPointF(5, 0)
        self.painter.drawText(label_location, tile.label)

    def _draw_hex(self, hex: Hex, color: QColor) -> None:
        """Draws a Tile background in the given color"""
        brush = QBrush(color)
        self.painter.setBrush(brush)
        self.painter.setPen(QPen(Qt.GlobalColor.black, 2))
        self.painter.drawPolygon(*hex.corners)

    def _draw_track_group(self, hex: Hex, group: list[Track]) -> None:
        """Draws a list of tracks together so that the outlines don't overlap."""
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
        """Returns a path along which a given Track should be drawn."""
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

    def _group_tracks(self, tracks: list[Track]) -> list[list[Track]]:
        """Groups tracks going to the same town into batches that will get drawn together."""

        outside: list[Track] = []
        inside = defaultdict(list)
        for a, b in tracks:
            if a.outside and b.outside:
                outside.append(
                    (a, b)
                )  # ! Does not properly allow for rendering bridges on cityless tiles.
            else:
                inside_dir = a if a.inside else b  # only one will be inside
                inside[inside_dir].append((a, b))

        sorted_inside = [
            inside[dir] for dir in sorted(inside.keys(), key=lambda d: d.value)
        ]
        if len(outside) > 0:
            sorted_inside.append(outside)

        return sorted_inside

    def _draw_city(self, hex: Hex, city: RevenueCenter, group: list[Track]) -> None:
        """Draws a city or a town on the hex."""
        location = hex.track_exit(Direction.C)

        if group:
            a, b = group[0]
            location = hex.track_exit(a) if a.inside else hex.track_exit(b)

        if isinstance(city, Town):
            self.painter.setBrush(QBrush(Qt.GlobalColor.black))
            self.painter.drawEllipse(location, TOWN_RADIUS, TOWN_RADIUS)
        elif isinstance(city, City):
            self.painter.setBrush(QBrush(Qt.GlobalColor.white))
            points = []
            if city.size == 1:
                points = [location]
            elif city.size == 2:
                points = [
                    QPointF(location.x() - CITY_RADIUS, location.y()),
                    QPointF(location.x() + CITY_RADIUS, location.y()),
                ]
            elif city.size == 3:
                points = [
                    QPointF(
                        location.x() - CITY_RADIUS, location.y() + CITY_RADIUS * 0.5
                    ),
                    QPointF(
                        location.x() + CITY_RADIUS, location.y() + CITY_RADIUS * 0.5
                    ),
                    QPointF(location.x(), location.y() - CITY_RADIUS * 1.2),
                ]
            else:
                raise ValueError("City has too many stations to draw than should be possible.")

            for pt in points:
                self.painter.drawEllipse(pt, CITY_RADIUS, CITY_RADIUS)

        # ? Consider doing this after rewrite to Tile.Segment
        # ! The values will overlap if there are two cities!!!
        value_location = lerp(hex.center, hex.corners[0], 0.65) - QPointF(5, 0)
        self.painter.drawText(value_location, str(city.value))
