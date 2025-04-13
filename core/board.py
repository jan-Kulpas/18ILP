from __future__ import annotations
import json

from dataclasses import dataclass
from typing import Any, ItemsView

from core.hex import Hex
from core.tile import TILES, Tile

BOARD_PATH = "data/{}/board.json"


@dataclass
class Field:
    tile: Tile
    # TODO: Tokens: list[Token]?


class Board:
    def __init__(self, year: str) -> None:
        self.year: str = year

        with open(BOARD_PATH.format(self.year)) as file:
            data: dict[str, Any] = json.load(file)

        self.preprinted_tiles: dict[str, Tile] = self._load_preprinted(data)
        self._board: dict[Hex, Field] = self._load_board(data)

        # // print(self.preprinted_tiles)

    def items(self) -> ItemsView[Hex, Field]:
        return self._board.items()

    def _load_board(self, data: dict[str, Any]) -> dict[Hex, Field]:
        shape: dict[str, list[list[int]]] = data["shape"]
        preprinted_locations: dict[str, str] = data["preprinted"]
        map: dict[Hex, Field] = {}

        # Generate empty fields for entire map
        for column, chunks in shape.items():
            for chunk in chunks:
                start = chunk[0]
                length = chunk[1]
                for row in range(start, start + length * 2, 2):
                    hex = Hex.from_string(f"{column}{row}")
                    # // print(f"{column}{row} -> {hex}")
                    map[hex] = Field(Tile.blank())

        # Add preprinted tiles at specified locations
        for coord, tile_id in preprinted_locations.items():
            hex = Hex.from_string(coord)
            tile = self.preprinted_tiles[tile_id]
            map[hex].tile = tile

        return map

    def _load_preprinted(self, data: dict[str, Any]) -> dict[str, Any]:
        return {tile["id"]: Tile.from_dict(tile) for tile in data["tiles"]}

    def __getitem__(self, key: Hex) -> Field:
        return self._board[key]

    def __repr__(self) -> str:
        return repr(self._board)
