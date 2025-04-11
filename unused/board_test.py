import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QPointF

HEX_SIZE = 80
WIDTH = 800
HEIGHT = 600

# Example axial coordinates
hex_coords = [(0, 0), (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1)]


def hex_to_pixel(q, r, size):
    x = size * 3 / 2 * q
    y = size * math.sqrt(3) * (r + q / 2)
    return x + WIDTH / 2, y + HEIGHT / 2


def polygon_corners(center_x, center_y, size):
    return [
        QPointF(
            center_x + size * math.cos(math.pi / 3 * i),
            center_y + size * math.sin(math.pi / 3 * i),
        )
        for i in range(6)
    ]


def edge_midpoints(center_x, center_y, size):
    corners = polygon_corners(center_x, center_y, size)
    midpoints = []
    for i in range(6):
        a = corners[i]
        b = corners[(i + 1) % 6]
        mid = QPointF((a.x() + b.x()) / 2, (a.y() + b.y()) / 2)
        midpoints.append(mid)
    return midpoints


class HexTile:
    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.selected = False
        self.center = hex_to_pixel(q, r, HEX_SIZE)
        self.corners = polygon_corners(*self.center, HEX_SIZE)
        self.edge_midpoints = edge_midpoints(*self.center, HEX_SIZE)
        self.tracks = []  # List of (start_edge, end_edge)

    def contains_point(self, point):
        px, py = point.x(), point.y()
        cx, cy = self.center
        return math.hypot(px - cx, py - cy) < HEX_SIZE * 1.1

    def add_track(self, start_edge, end_edge):
        if (start_edge, end_edge) not in self.tracks and (
            end_edge,
            start_edge,
        ) not in self.tracks:
            self.tracks.append((start_edge, end_edge))

    def draw(self, painter):
        brush = (
            QBrush(QColor(200, 100, 100))
            if self.selected
            else QBrush(QColor(230, 230, 230))
        )
        painter.setBrush(brush)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawPolygon(*self.corners)

        # Draw tracks with more curve
        pen = QPen(Qt.GlobalColor.darkGreen, 4)
        painter.setPen(pen)
        for start_edge, end_edge in self.tracks:
            start = self.edge_midpoints[start_edge]
            end = self.edge_midpoints[end_edge]
            cx, cy = self.center
            center = QPointF((start.x() + end.x()) / 2, (start.y() + end.y()) / 2)

            # Make the curve more pronounced by pulling control point toward center *more*
            pull_strength = 0.75  # Try 1.5 to 2.5 for more curve
            ctrl_x = center.x() + (cx - center.x()) * pull_strength
            ctrl_y = center.y() + (cy - center.y()) * pull_strength
            ctrl = QPointF(ctrl_x, ctrl_y)

            path = QPainterPath()
            path.moveTo(start)
            path.quadTo(ctrl, end)
            painter.drawPath(path)


class HexBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hex Board with Tracks")
        self.setGeometry(100, 100, WIDTH, HEIGHT)
        self.tiles = [HexTile(q, r) for q, r in hex_coords]

        # Add some sample tracks to demonstrate
        self.tiles[0].add_track(0, 5)  # from top to bottom
        self.tiles[1].add_track(0, 3)
        self.tiles[2].add_track(2, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for tile in self.tiles:
            tile.draw(painter)

    def mousePressEvent(self, event):
        pos = event.pos()
        for tile in self.tiles:
            if tile.contains_point(pos):
                tile.selected = not tile.selected
                self.update()
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HexBoard()
    window.show()
    sys.exit(app.exec_())
