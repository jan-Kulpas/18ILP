from __future__ import annotations

import math
import re
from dataclasses import dataclass

from PyQt6.QtCore import QPoint, QPointF

from core.tile import Direction
from gui.helpers import lerp

SIZE = 50


@dataclass(eq=True, frozen=True)
class Hex:
    """
    Represents a point in a hexagonal grid. Uses cubic coordinates.
    """

    q: int
    r: int
    s: int

    @classmethod
    def from_doubled(cls, x: int, y: int) -> Hex:
        """Creates a Hex from Double-Height coordinates"""
        # TODO: Move out the offset to renderer to make 0th hex match
        q = x
        r = (y - x) // 2 + 1  # ! Offset makes Doubled(0,0) mismatch with Cubic(0,0,0)!
        return cls(q, r, -q - r)

    @classmethod
    def from_string(cls, s: str) -> Hex:
        """
        Creates a Hex from a string describing Double-Height coordinates.

        e.g. Hex.from_string("C4") is equivalent to Hex.from_doubled(3,4).
        Column A is considered index 1.

        Params:
            s (str): Double-Height coordinate. Letter part signifies the column and number signifies the row.
        Raises:
            ValueError: Input string did not map to a valid coordinate.
        """
        match = re.fullmatch(r"([A-Z]+)(\d+)", s)
        if not match:
            raise ValueError(f"Input string did not map to a valid coordinate: {s}")

        col_str, row_str = match.groups()

        # Convert letters to number: e.g., AA -> 27
        col = 0
        for char in col_str:
            col = col * 26 + (ord(char) - ord("A") + 1)

        row = int(row_str)
        return cls.from_doubled(col, row)

    @classmethod
    def from_pixel(cls, p: QPoint) -> Hex:
        """Returns a Hex from a QPoint by checking in which hex in the grid it would lie"""
        q = (2 / 3 * p.x()) / SIZE
        r = (-1 / 3 * p.x() + math.sqrt(3) / 3 * p.y()) / SIZE
        return Hex.from_cubic_float(q, r, -q - r)

    @classmethod
    def from_cubic_float(cls, fq: float, fr: float, fs: float) -> Hex:
        """Returns a Hex from 3 floats by rounding them to the nearest integer Cubic coordinates."""
        q = round(fq)
        r = round(fr)
        s = round(fs)

        q_diff = abs(q - fq)
        r_diff = abs(r - fr)
        s_diff = abs(s - fs)

        if q_diff > r_diff and q_diff > s_diff:
            q = -r - s
        elif r_diff > s_diff:
            r = -q - s
        else:
            s = -q - r

        return Hex(q, r, s)

    def neighbour(self, dir: Direction) -> Hex:
        """
        Returns a Hex neighbouring this Hex in the specified direction.
        """
        return self + UNITS[dir.value]

    @property
    def center(self) -> QPointF:
        """The center pixel of the Hex."""
        x = SIZE * (3 / 2 * self.q)
        y = SIZE * (math.sqrt(3) / 2 * self.q + math.sqrt(3) * self.r)
        return QPointF(x, y)

    @property
    def corners(self) -> list[QPointF]:
        """Corner pixels of the Hex. 0th index is first corner clockwise from midnight."""
        return [
            self.center
            + QPointF(
                SIZE * math.cos(math.pi / 3 * (i - 1)),
                SIZE * math.sin(math.pi / 3 * (i - 1)),
            )
            for i in range(6)
        ]

    @property
    def midpoints(self) -> list[QPointF]:
        """Midpoint pixels of Hex edges. 0th index is the upper edge. Goes clockwise."""

        return [lerp(self.corners[i], self.corners[(i - 1) % 6], 0.5) for i in range(6)]

    @property
    def citypoints(self) -> list[QPointF]:
        """Center pixels of cities R1-R6 on the tile, 0th index is first point clockwise starting *with* midnight."""
        return [self.center] + [lerp(self.midpoints[i], self.center, 0.5) for i in range(6)]

    # def track_exit(self, dir: Direction):
    #     """
    #     Returns either a midpoint, a citypoint or the hex center based on Direction.

    #     The ending pixel of a track path.
    #     """
    #     # ! This ties the city position to the json data which should be avoided.
    #     if dir.outside:
    #         return self.midpoints[dir.value]
    #     elif dir == Direction.C:
    #         return self.center
    #     else:
    #         return self.citypoints[dir.value - 6]

    def __add__(self, other: Hex) -> Hex:
        return Hex(self.q + other.q, self.r + other.r, self.s + other.s)

    def __str__(self) -> str:
        col = self.q
        row = 2 * self.r + self.q
        return f"Hex({chr(ord('A')+col-1)}{row-1})"


UNITS = [
    Hex(0, -1, 1),
    Hex(1, -1, 0),
    Hex(1, 0, -1),
    Hex(0, 1, -1),
    Hex(-1, 1, 0),
    Hex(-1, 0, 1),
]
