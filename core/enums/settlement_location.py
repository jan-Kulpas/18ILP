from __future__ import annotations
from enum import Enum


class SettlementLocation(Enum):
    C = 0 # Center for Lawsonian tiles
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6

    def rotated(self, r: int) -> SettlementLocation:
        if self == SettlementLocation.C:
            return self
        else:
            value = ((self.value - 1) + r) % (len(SettlementLocation) - 1) + 1
            return SettlementLocation(value)
