import json

from enum import Enum, Flag
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Self


class Direction(Enum):
    NE = 1
    SE = 2
    S = 3
    SW = 4
    NW = 5
    N = 6
    # Center for Lawsonian tiles:
    C = 0
    # Revenue center indexes
    R1 = -1
    R2 = -2
    R3 = -3
    R4 = -4
    R5 = -5
    R6 = -6


class Color(Flag):
    """
    Tile color, can be combined bitwise to represent multiple colors
    """

    BLANK = 0
    YELLOW = 1
    GREEN = 2
    BROWN = 4
    GRAY = 8


@dataclass(frozen=True)
class Town:
    value: int = 10


@dataclass(frozen=True)
class City:
    value: int
    size: int


@dataclass(frozen=True)
class Tile:
    """
    Represents a single tile.

    Note that this doesn't contain info on the position on board but the contents of the tile.
    """

    id: str
    tracks: list[tuple[Direction, Direction]]
    color: Color
    cities: list[City | Town] = field(default_factory=list)
    label: str | None = None
    upgrades: list[str] = field(default_factory=list)

    @property
    def json(self):
        return json.dumps(self, cls=_TileEncoder)

    @classmethod
    def from_json(cls, string) -> Self:
        return json.loads(string, object_hook=decode_tile)


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


def decode_tile(dct: dict) -> Any:
    if "value" in dct:
        if "size" in dct:
            return City(value=dct["value"], size=dct["size"])
        else:
            return Town(value=dct["value"])
    if "id" in dct:
        return Tile(
            id=dct["id"],
            tracks=[(Direction[pair[0]], Direction[pair[1]]) for pair in dct["tracks"]],
            color=Color(sum([Color[name].value for name in dct["color"]])),
            cities=dct["cities"],
            label=dct["label"],
            upgrades=dct["upgrades"],
        )
