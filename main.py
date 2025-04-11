import sys

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QPointF


from core.tile import *
from core.game import *
from core.tile_manifest import TileManifest
from core.hex import Hex

WIDTH = 1200
HEIGHT = 800

class Drawer:
    @staticmethod
    def draw_tile(painter: QPainter, hex: Hex, tile: Tile) -> None:
        brush = QBrush(QColor(230, 230, 230))
        painter.setBrush(brush)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawPolygon(*hex.corners)

        painter.drawText(hex.center, str(hex))

        # Draw tracks with more curve
        # pen = QPen(Qt.GlobalColor.darkGreen, 4)
        # painter.setPen(pen)
        # for start_edge, end_edge in hex.tracks:
        #     start = hex.edge_midpoints[start_edge]
        #     end = hex.edge_midpoints[end_edge]
        #     cx, cy = hex.center
        #     center = QPointF((start.x() + end.x()) / 2, (start.y() + end.y()) / 2)

        #     # Make the curve more pronounced by pulling control point toward center *more*
        #     pull_strength = 0.75  # Try 1.5 to 2.5 for more curve
        #     ctrl_x = center.x() + (cx - center.x()) * pull_strength
        #     ctrl_y = center.y() + (cy - center.y()) * pull_strength
        #     ctrl = QPointF(ctrl_x, ctrl_y)

        #     path = QPainterPath()
        #     path.moveTo(start)
        #     path.quadTo(ctrl, end)
        #     painter.drawPath(path)

class Window(QWidget):
    def __init__(self, game: Game):
        super().__init__()
        self.setWindowTitle("18xx-router")
        self.setGeometry(100, 100, WIDTH, HEIGHT)
        self.game = game
        # self.tiles = [HexTile(q, r) for q, r in hex_coords]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for hex, tile in self.game.board.board.items():
            Drawer.draw_tile(painter,hex,tile)

    def mousePressEvent(self, event):
        pos = event.pos()
        print(pos)
        # for tile in self.tiles:
        #     if tile.contains_point(pos):
        #         tile.selected = not tile.selected
        #         self.update()
        #         break


if __name__ == "__main__":
    game = Game("1889")

    app = QApplication(sys.argv)
    window = Window(game)
    window.show()


    print(game.board.board)
    sys.exit(app.exec())
