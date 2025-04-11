from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum, Flag
import json

from pydantic import BaseModel


class Direction(Enum):
    NE = 1
    SE = 2
    S = 3
    SW = 4
    NW = 5
    N = 6


class Color(Flag):
    """
    Tile color, can be combined bitwise to represent multiple colors
    """

    BLANK = 0
    YELLOW = 1
    GREEN = 2
    BROWN = 4
    GRAY = 8


class Town(BaseModel):
    value: int = 10


class City(BaseModel):
    value: int
    size: int


class Tile(BaseModel):
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

    class Config:
        json_encoders = {Direction: lambda dir: dir.name}
