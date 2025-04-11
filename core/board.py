from __future__ import annotations
import json
import re

from dataclasses import dataclass
from typing import Any

from core.hex import Hex
from core.tile import TILES, Tile

BOARD_PATH = "data/{}/board.json"

# @dataclass(eq=True, frozen=True)
# class Coord:
#     col: int
#     row: int

#     @classmethod
#     def from_string(cls, s: str) -> Coord:
#         match = re.fullmatch(r'([A-Z]+)(\d+)', s)
#         if not match:
#             raise ValueError(f"Invalid cell format: {s}")

#         col_str, row_str = match.groups()

#         # Convert letters to number: e.g., AA -> 27
#         col = 0
#         for char in col_str:
#             col = col * 26 + (ord(char) - ord('A') + 1)

#         row = int(row_str)
#         return cls(col, row)

#     def __str__(self) -> str:
#         return f"{chr(ord('A')+self.col-1)}{self.row}"

#     def __repr__(self) -> str:
#         return f"Coord({chr(ord('A')+self.col-1)}{self.row})"


@dataclass
class Field:
    pass


class Board:
    def __init__(self, year: str) -> None:
        self.year: str = year
        self.board: dict[Hex, Tile] = self._load_board()

    def _load_board(self) -> dict[Hex, Tile]:
        map: dict[Hex, Tile] = {}

        with open(BOARD_PATH.format(self.year)) as file:
            data: dict[str, Any] = json.load(file)
            shape: dict[str, list[list[int]]] = data["shape"]

            for column, chunks in shape.items():
                for chunk in chunks:
                    start = chunk[0]
                    length = chunk[1]
                    for row in range(start, start + length * 2, 2):
                        coord = Hex.from_string(f"{column}{row}")
                        print(f"{column}{row} -> {coord}")
                        map[coord] = Tile.blank()
        return map
