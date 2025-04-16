from collections import namedtuple
from pprint import pprint

from core.railroad import Train
from core.tile import *

MANIFEST_PATH = "data/{}/manifest.json"


class Manifest:
    """Tile Manifest is responsible for keeping track which tiles and how many of them are availble to be placed in game."""

    def __init__(self, year: str) -> None:
        self.year: str = year

        with open(MANIFEST_PATH.format(self.year)) as file:
            data: dict[str, Any] = json.load(file)

        self.tiles: dict[str, int] = self._load_tiles(data)
        self.trains: dict[str, int] = self._load_trains(data)

    def _load_tiles(self, data: dict[str, Any]) -> dict[str, int]:
        return {key: int(value) for key, value in data["tiles"].items()}

    def _load_trains(self, data: dict[str, Any]) -> dict[str, int]:
        return {key: int(value) for key, value in data["trains"].items()}

    def __str__(self) -> str:
        return str({"tiles": self.tiles, "trains": self.trains})
