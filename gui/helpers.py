from PyQt6.QtCore import QPointF


def lerp(a: QPointF, b: QPointF, t: float) -> QPointF:
    return a + (b - a) * t
