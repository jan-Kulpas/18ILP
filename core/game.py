from core.tile_manifest import TileManifest
from core.board import Board


class Game:
    def __init__(self, year: str) -> None:
        self.year = year
        self.manifest = TileManifest(year)
        self.board = Board(year)
