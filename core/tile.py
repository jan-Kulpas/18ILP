from __future__ import annotations
from abc import ABC
import json

from enum import Enum, Flag
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any

from core.settlement import City, Settlement, Town

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

class SettlementLocation(Enum):
    C = 0 # Center for Lawsonian tiles
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6


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

@dataclass(frozen=True)
class Segment:
    tracks: list[Direction] = field(default_factory=list)
    settlement: Settlement | None = field(default=None)
    location: SettlementLocation | None = field(default=None)
    
    @classmethod
    def from_json(cls, string: str) -> Segment:
        dict = json.loads(string)
        return Segment.from_dict(dict)
    
    @classmethod
    def from_dict(cls, dict: dict) -> Segment:
        if "tracks" in dict:
            dict["tracks"] = [Direction[dir] for dir in dict["tracks"]]
        if "settlement" in dict:
            dict["settlement"] = Settlement.from_dict(dict["settlement"])
        if "location" in dict:
            dict["location"] = SettlementLocation[dict["location"]]
        
        return Segment(**dict)

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
    color: Color = field()
    segments: list[Segment] = field(default_factory=list)
    label: str | None = field(default=None, compare=False)
    upgrades: list[str] = field(default_factory=list, compare=False)

    @classmethod
    def blank(cls) -> Tile:
        return cls("0", Color.BLANK, upgrades=["7", "8", "9"])

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
            dict["cities"] = [Settlement.from_dict(city_dict) for city_dict in dict["cities"]]
        if "segments" in dict:
            dict["segments"] = [Segment.from_dict(segment) for segment in dict["segments"]]
        
        return Tile(
            id=dict["id"],
            color=Color(sum([Color[name].value for name in dict["color"]])),
            **{k: dict[k] for k in ["segments", "label", "upgrades"] if k in dict},
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