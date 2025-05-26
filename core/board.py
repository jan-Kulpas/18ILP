from __future__ import annotations
from collections.abc import Iterator
import json
from typing import TYPE_CHECKING, Any, ItemsView

from core.hex import Hex
from core.railway import Railway
from core.settlement import Settlement
from core.tile import Segment, Tile

if TYPE_CHECKING:
    from solver.graph import CityNode

BOARD_PATH = "data/{}/board.json"


class Board:
    def __init__(self, year: str) -> None:
        self.year: str = year

        with open(BOARD_PATH.format(self.year)) as file:
            data: dict[str, Any] = json.load(file)

        self.preprinted_tiles: dict[str, Tile] = self._load_preprinted(data)
        self._board: dict[Hex, Tile] = self._load_board(data)

        # // print(self.preprinted_tiles)

    def items(self) -> ItemsView[Hex, Tile]:
        return self._board.items()

    def segment_at(self, node: CityNode) -> Segment:

        return self[node.hex].segment_at(node.loc)

    def settlement_at(self, node: CityNode) -> Settlement:
        settlement = self.segment_at(node).settlement
        if not settlement:
            raise IndexError(f"No settlement at specified coordinate: {node}")
        return settlement

    # TODO: Take railways to separate file and move this up to Game class.
    def load_railways(self) -> dict[str, Railway]:
        with open(BOARD_PATH.format(self.year)) as file:
            data: dict[str, Any] = json.load(file)

        return {dct["id"]: Railway.from_dict(dct) for dct in data["railways"]}

    def _load_board(self, data: dict[str, Any]) -> dict[Hex, Tile]:
        shape: dict[str, list[list[int]]] = data["shape"]
        preprinted_locations: dict[str, str] = data["preprinted"]
        map: dict[Hex, Tile] = {}

        # Generate empty fields for entire map
        for column, chunks in shape.items():
            for chunk in chunks:
                start = chunk[0]
                length = chunk[1]
                for row in range(start, start + length * 2, 2):
                    hex = Hex.from_string(f"{column}{row}")
                    # // print(f"{column}{row} -> {hex}")
                    map[hex] = Tile.blank()

        # Add preprinted tiles at specified locations
        for coord, tile_id in preprinted_locations.items():
            hex = Hex.from_string(coord)
            tile = self.preprinted_tiles[tile_id]
            map[hex] = tile

        return map

    def _load_preprinted(self, data: dict[str, Any]) -> dict[str, Any]:
        return {tile["id"]: Tile.from_dict(tile) for tile in data["tiles"]}

    def __getitem__(self, key: Hex) -> Tile:
        return self._board[key]

    def __setitem__(self, key: Hex, value: Tile):
        self._board[key] = value

    def __iter__(self) -> Iterator[Hex]:
        return iter(self._board)

    def __repr__(self) -> str:
        return repr(self._board)
