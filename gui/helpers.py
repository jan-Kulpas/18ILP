import random

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor

def lerp(a: QPointF, b: QPointF, t: float) -> QPointF:
    return a + (b - a) * t

def random_color() -> QColor:
    return QColor.fromHsl(random.randrange(0,360), random.randrange(107,250), random.randrange(102, 230))

def node2point(node: str) -> QPointF:
    from core.enums.direction import Direction
    from core.enums.settlement_location import SettlementLocation
    from core.hex import Hex


    if "." in node:
        hex, loc = node.split(".")
        return Hex.from_string(hex).citypoints[SettlementLocation[loc].value]
    elif "-" in node:
        hex1, hex2 = (Hex.from_string(s) for s in node.split("-"))
        direction = Direction.from_unit_hex(hex2 - hex1)
        return hex1.midpoints[direction.value]
    raise NotImplementedError("We dont know how to draw junctions")
