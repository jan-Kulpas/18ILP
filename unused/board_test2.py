import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QPointF

HEX_SIZE = 40
WIDTH = 800
HEIGHT = 600


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


# --- Basic Classes ---


class Hex:
    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.center = hex_to_pixel(q, r, HEX_SIZE)
        self.corners = polygon_corners(*self.center, HEX_SIZE)


class Tile:
    def __init__(self, terrain_type):
        self.terrain_type = terrain_type

    def color(self):
        return {
            "grass": QColor(120, 200, 120),
            "water": QColor(80, 150, 220),
            "mountain": QColor(130, 130, 130),
        }.get(self.terrain_type, QColor(240, 240, 240))


class Field:
    def __init__(self, hex: Hex, tile: Tile):
        self.hex = hex
        self.tile = tile


# --- Renderer ---


class FieldRenderer:
    def draw(self, painter, field: Field):
        hex = field.hex
        tile = field.tile

        # Draw tile background
        painter.setBrush(QBrush(tile.color()))
        painter.setPen(QPen(Qt.black, 2))
        painter.drawPolygon(*hex.corners)

        # Optional: Draw text
        painter.setPen(Qt.black)
        painter.drawText(
            int(hex.center[0] - 10),
            int(hex.center[1] + 5),
            tile.terrain_type.capitalize(),
        )


# --- Main Widget ---


class HexBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hex Renderer Example")
        self.setGeometry(100, 100, WIDTH, HEIGHT)

        self.fields = self.create_fields()
        self.renderer = FieldRenderer()

    def create_fields(self):
        coords = [(0, 0), (1, 0), (0, 1), (-1, 1)]
        types = ["grass", "water", "mountain", "grass"]
        return [Field(Hex(q, r), Tile(t)) for (q, r), t in zip(coords, types)]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for field in self.fields:
            self.renderer.draw(painter, field)


# --- App ---

if __name__ == "__main__":
    app = QApplication(sys.argv)
    board = HexBoard()
    board.show()
    sys.exit(app.exec_())
