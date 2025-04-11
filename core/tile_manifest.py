import csv
from pprint import pprint
from core.tile import *

TILE_MANIFEST_PATH = "data/{}/manifest.csv"


class TileManifest:
    def __init__(self, year: str) -> None:
        self.year: str = year
        self._tiles: dict[Tile, int] = self._load_tiles()

    def _load_tiles(self) -> dict[Tile, int]:
        with open(TILE_MANIFEST_PATH.format(self.year)) as file:
            reader = csv.reader(file)
            return {TILES[row[0]]: int(row[1]) for row in reader}

    def __str__(self) -> str:
        return str({tile.id: count for tile, count in self._tiles.items()})

    def __repr__(self) -> str:
        return repr(self._tiles)
