from __future__ import annotations

import math
import re
from dataclasses import dataclass

from PyQt6.QtCore import QPoint, QPointF

from core.tile import Direction

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
        print(x)
        q = x
        r = (y - x) // 2 + 1
        return cls(q, r, -q - r)

    @classmethod
    def from_string(cls, s: str) -> Hex:
        """
        Creates a Hex from a string describing Double-Height coordinates.
        e.g. Hex.from_string("C4") is equivalent to Hex.from_doubled(3,4).
        Column A is considered index 1.
        """
        match = re.fullmatch(r"([A-Z]+)(\d+)", s)
        if not match:
            raise ValueError(f"Invalid format: {s}")

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

    def neighbour(self, dir: Direction):
        return self + UNITS[dir.value]

    @property
    def center(self) -> QPointF:
        x = SIZE * (3 / 2 * self.q)
        y = SIZE * (math.sqrt(3) / 2 * self.q + math.sqrt(3) * self.r)
        return QPointF(x, y)

    @property
    def corners(self) -> list[QPointF]:
        return [
            self.center
            + QPointF(
                SIZE * math.cos(math.pi / 3 * i), SIZE * math.sin(math.pi / 3 * i)
            )
            for i in range(6)
        ]

    @property
    def midpoints(self) -> list[QPointF]:
        def lerp(a: QPointF, b: QPointF, t: float) -> QPointF:
            return a + (b - a) * t

        return [lerp(self.corners[i], self.corners[(i + 1) % 6], 0.5) for i in range(6)]

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

print(Hex.from_cubic_float(1.4, 3.1, 6.7))
