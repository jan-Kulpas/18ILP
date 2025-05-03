from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from core.hex import Hex


class Direction(Enum):
    """
    Direction in which a track may go, i.e. edges of a hex.
    """

    N = 0
    NE = 1
    SE = 2
    S = 3
    SW = 4
    NW = 5

    def rotated(self, r: int) -> Direction:
        return Direction((self.value + r) % len(Direction))

    def invert(self) -> Direction:
        return self.rotated(3)

    @classmethod
    def from_unit_hex(cls, hex: Hex):
        from core.hex import UNITS

        return Direction(UNITS.index(hex))
