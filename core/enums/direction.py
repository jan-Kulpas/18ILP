from __future__ import annotations
from enum import Enum

class Direction(Enum):
    """
    Direction in which a track may go, i.e. edges of a hex or revenue centers located on it.
    """
    N = 0
    NE = 1
    SE = 2
    S = 3
    SW = 4
    NW = 5

    def rotated(self, r: int) -> Direction:
        return Direction((self.value + r) % len(Direction))