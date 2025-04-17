from __future__ import annotations
from abc import ABC
import json

from enum import Enum, Flag
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any

from core.revenue_center import City, RevenueCenter, Town

# TODO: Replace with Segment containing root city and branching outside edges.
type Track = tuple[Direction, Direction]


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
    # Revenue center indexes
    R1 = 6
    R2 = 7
    R3 = 8
    R4 = 9
    R5 = 10
    R6 = 11
    # Center for Lawsonian tiles:
    C = 12

    @property
    def outside(self) -> bool:
        """Checks if direction points to a tile border"""
        return self.value >= 0 and self.value <= 5

    @property
    def inside(self) -> bool:
        """Checks if direction points to a city or a junction within a tile"""
        return not self.outside


class Color(Flag):
    """
    Tile color, can be combined bitwise to represent multiple colors
    """

    BLANK = 0
    YELLOW = 1
    GREEN = 2
    BROWN = 4
    GRAY = 8
    RED = 16


@dataclass(eq=True, frozen=True)
class Tile:
    """
    A single tile that can be placed on the board.

    Note that this doesn't contain info on the position on board but the contents of the tile.

    Attributes:
        id (str): ID printed on the tile.
        tracks (list[tuple[Direction, Direction]]): List of track segments made of a tuple containing the 2 endpoints of a curve.
        color (Color): Color of the tile, can be multiple colors using bitwise operations
        cities (list[RevenueCenter]): List of revenue centers printed on the tile.
        label (str): Alpha code printed on the tile.
        upgrades (list[str]): List of tile IDs that this tile could be upgraded to.
    """

    id: str = field()
    tracks: list[Track] = field(compare=False)
    color: Color = field()
    cities: list[RevenueCenter] = field(default_factory=list, compare=False)
    label: str | None = field(default=None, compare=False)
    upgrades: list[str] = field(default_factory=list, compare=False)

    @classmethod
    def blank(cls) -> Tile:
        return cls("0", [], Color.BLANK, upgrades=["7", "8", "9"])

    @classmethod
    def from_id(cls, id: str) -> Tile:
        from core.database import Database

        return Database().tiles[id]

    @classmethod
    def from_json(cls, string: str) -> Tile:
        dict = json.loads(string)
        return Tile.from_dict(dict)
    
    @classmethod
    def from_dict(cls, dict: dict) -> Tile:
        if "cities" in dict:
            dict["cities"] = [RevenueCenter.from_dict(city_dict) for city_dict in dict["cities"]]
        return Tile(
            id=dict["id"],
            tracks=[(Direction[pair[0]], Direction[pair[1]]) for pair in dict["tracks"]],
            color=Color(sum([Color[name].value for name in dict["color"]])),
            **{k: dict[k] for k in ["cities", "label", "upgrades"] if k in dict},
        )

    
    @property
    def json(self):
        return json.dumps(self, cls=_TileEncoder)


class _TileEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Color):
            flags = []
            for flag in obj:
                flags.append(flag.name)
            if not flags:
                return [Color.BLANK.name]
            return flags
        elif isinstance(obj, Enum):
            return obj.name
        elif is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)
        elif isinstance(obj, tuple):
            return list(obj)
        return super().default(obj)