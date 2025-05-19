from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from core.enums.settlement_location import SettlementLocation
from core.hex import Hex


class Node(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass


@dataclass(frozen=True, eq=True)
class CityNode(Node):
    hex: Hex = field()
    loc: SettlementLocation = field()

    def __str__(self) -> str:
        return f"{self.hex}.{self.loc.name}"


@dataclass(frozen=True, eq=True)
class JunctionNode(Node):
    hexes: tuple[Hex, Hex] = field()

    def __post_init__(self):
        if str(self.hexes[0]) > str(self.hexes[1]):
            object.__setattr__(self, "hexes", (self.hexes[1], self.hexes[0]))

    def __iter__(self):
        return iter(self.hexes)

    def __str__(self) -> str:
        return f"{self.hexes[0]}-{self.hexes[1]}"


@dataclass(frozen=True, eq=True)
class Edge:
    nodes: tuple[Node, Node] = field()
    hex: Hex = field()

    def __post_init__(self):
        if str(self.nodes[0]) > str(self.nodes[1]):
            object.__setattr__(self, "nodes", (self.nodes[1], self.nodes[0]))

    def __iter__(self):
        return iter(self.nodes)

    def __str__(self) -> str:
        return f"({self.nodes[0]}, {self.nodes[1]})"
