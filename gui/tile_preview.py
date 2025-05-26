from PyQt6.QtWidgets import (
    QListWidgetItem,
)
from PyQt6.QtGui import (
    QPixmap,
    QImage,
    QIcon,
)
from PyQt6.QtCore import Qt, QSize

from core.game import Game
from core.hex import Hex
from core.tile import Tile
from gui.renderer import Renderer


class TilePreview(QListWidgetItem):
    game: Game
    tile: Tile
    size: QSize

    def __init__(self, game: Game, tile: Tile, size: QSize = QSize(100, 100)):
        super().__init__()
        self.game = game
        self.tile = tile
        self.size = size

        self.updateIcon()

        self.setText(tile.id)

    def updateIcon(self) -> None:
        image = QImage(self.size, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)

        renderer = Renderer(self.game.year, image)
        renderer.draw_tile(Hex(0.7, 0.3, -1), self.tile)

        pixmap = QPixmap.fromImage(image)
        self.setIcon(QIcon(pixmap))
