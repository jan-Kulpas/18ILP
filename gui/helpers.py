from __future__ import annotations

import random
from typing import TYPE_CHECKING

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor

if TYPE_CHECKING:
    from solver.graph import Node


def lerp(a: QPointF, b: QPointF, t: float) -> QPointF:
    return a + (b - a) * t


def random_color() -> QColor:
    return QColor.fromHsl(
        random.randrange(0, 360), random.randrange(107, 250), random.randrange(102, 230)
    )


def node2point(node: Node) -> QPointF:
    from core.enums.direction import Direction
    from solver.graph import CityNode, JunctionNode

    match node:
        case CityNode():
            return node.hex.citypoints[node.loc.value]
        case JunctionNode():
            hex1, hex2 = node
            direction = Direction.from_unit_hex(hex2 - hex1)
            return hex1.midpoints[direction.value]

    raise NotImplementedError("We dont know how to draw junctions")
