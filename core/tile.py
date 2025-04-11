from __future__ import annotations
import json

from enum import Enum, Flag
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any


class Direction(Enum):
    """
    Enum representing direction in which a track may go
    i.e. edges of a hex or revenue centers located on it.
    """

    N = 0
    NE = 1
    SE = 2
    S = 3
    SW = 4
    NW = 5
    # Revenue center indexes
    R1 = -1
    R2 = -2
    R3 = -3
    R4 = -4
    R5 = -5
    R6 = -6
    # Center for Lawsonian tiles:
    C = -7


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
class Town:
    value: int = 10


@dataclass(frozen=True)
class City:
    value: int
    size: int


@dataclass(eq=True, frozen=True)
class Tile:
    """
    Represents a single tile.

    Note that this doesn't contain info on the position on board but the contents of the tile.

    Attributes:
        id (str): ID printed on the tile.
        tracks (list[tuple[Direction, Direction]]): List of track segments made of a tuple containing the 2 endpoints of a curve.
        color (Color): Color of the tile, can be multiple colors using bitwise operations
        cities (list[City | Town]): List of revenue centers printed on the tile.
        label (str): Alpha code printed on the tile.
        upgrades (list[str]): List of tile IDs that this tile could be upgraded to.
    """

    id: str = field()
    tracks: list[tuple[Direction, Direction]] = field(compare=False)
    color: Color = field()
    cities: list[City | Town] = field(default_factory=list, compare=False)
    label: str | None = field(default=None, compare=False)
    upgrades: list[str] = field(default_factory=list, compare=False)

    @classmethod
    def blank(cls) -> Tile:
        return cls("0", [], Color.BLANK, upgrades=["7", "8", "9"])

    @property
    def json(self):
        return json.dumps(self, cls=_TileEncoder)

    @classmethod
    def from_json(cls, string: str) -> Tile:
        return json.loads(string, object_hook=_decode_tile)

    @classmethod
    def from_dict(cls, dict: dict) -> Tile:
        return cls.from_json(json.dumps(dict))


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


def _decode_tile(dct: dict) -> Any:
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
            cities=dct["cities"] if "cities" in dct else [],
            label=dct["label"] if "label" in dct else None,
            upgrades=dct["upgrades"],
        )


TILE_DB_PATH = "data/tiles.json"

TILES: dict[str, Tile] = {
    tile["id"]: Tile.from_dict(tile) for tile in json.load(open(TILE_DB_PATH))
}
