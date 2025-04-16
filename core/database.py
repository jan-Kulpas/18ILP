from __future__ import annotations
from collections import namedtuple
from pprint import pprint

from core.railway import Train
from core.tile import *
from core.phase import Phase

TILE_DB_PATH = "data/tiles.json"
TRAIN_DB_PATH = "data/{}/trains.json"


class Database:
    """Singleton used for loading in tiles and trains from their id"""

    _instance = None

    def __new__(cls, year: str | None = None) -> Database:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, year: str | None = None) -> None:
        if hasattr(self, "_initialized"):
            return
        if year == None:
            raise ValueError(
                "First time initialization requires a year parameter passed."
            )

        self.year: str = year

        # TODO: load predefined tiles here too?
        self.tiles: dict[str, Tile] = self._load_tiles()
        self.trains: dict[str, Train] = self._load_trains()
        self.phases: dict[str, Phase] = self._load_phases()

        self._initialized = True

    def _load_tiles(self) -> dict[str, Tile]:
        return {
            tile["id"]: Tile.from_dict(tile) for tile in json.load(open(TILE_DB_PATH))
        }

    def _load_trains(self) -> dict[str, Train]:
        return {
            train["id"]: Train.from_dict(train)
            for train in json.load(
                open(TRAIN_DB_PATH.format(self.year)),
            )
        }

    # ? Consider doing a list for ordering
    def _load_phases(self) -> dict[str, Phase]:
        return {
            train["id"]: Phase.from_dict(
                {
                    "id": train["id"],
                    **train["phase"],
                }
            )
            for train in json.load(
                open(TRAIN_DB_PATH.format(self.year)),
            )
        }

    def __str__(self) -> str:
        return str({"tiles": self.tiles, "trains": self.trains})
