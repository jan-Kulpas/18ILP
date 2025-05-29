from __future__ import annotations
from collections import namedtuple
import json
from pprint import pprint
from typing import Any

from core.train import Train
from core.tile import Tile
from tools.exceptions import RuleError

MANIFEST_PATH = "data/{}/manifest.json"


class Bank:
    """
    The Bank is responsible for keeping track of the components available in the game
    """

    def __init__(self, year: str) -> None:
        self.year: str = year

        with open(MANIFEST_PATH.format(self.year)) as file:
            data: dict[str, Any] = json.load(file)

        self.tiles: dict[str, int] = self._load_tiles(data)
        self.trains: dict[str, int] = self._load_trains(data)

    def take_tile(self, tile: Tile) -> None:
        # Ignore debug tiles
        if tile.id.startswith("DBG"):
            return
        
        if self.tiles[tile.id] <= 0:
            raise RuleError(f"There are no more copies of this tile in the Bank: {tile.id}")
        self.tiles[tile.id] -= 1

    def take_train(self, train: Train) -> None:
        if self.trains[train.id] <= 0:
            raise RuleError(f"There are no more copies of this train in the Bank: {train.id}")
        self.trains[train.id] -= 1

    def _load_tiles(self, data: dict[str, Any]) -> dict[str, int]:
        return {key: int(value) for key, value in data["tiles"].items()}

    def _load_trains(self, data: dict[str, Any]) -> dict[str, int]:
        return {key: int(value) for key, value in data["trains"].items()}

    def __str__(self) -> str:
        return str({"tiles": self.tiles, "trains": self.trains})
