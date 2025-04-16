from __future__ import annotations
from dataclasses import dataclass, field
import json

from core.tile import Color


@dataclass(frozen=True)
class Train:
    """
    A train card. Describes how a train travels on the board.

    Attributes:
        id(str): Train type name.
        range(int | None): How many revenue centers can it visit.
        diesel(bool): Does it have infinite range?
    """

    id: str = field()
    # ? Consider using a property for range calculation
    range: int | None = field(default=None)

    # Powers
    diesel: bool = field(default=False)

    @classmethod
    def from_json(cls, string: str) -> Train:
        dict = json.loads(string)
        return Train.from_dict(dict)

    @classmethod
    def from_dict(cls, dict: dict) -> Train:
        keys = ["id", "range", "diesel"]
        return Train(**{k: dict[k] for k in keys if k in dict})


# ! order=True compares the ID which just happens to work for 1889 but may not for others!
# ? consider adding a postinit field that would be a counter of added phases and compare based on that
# ? or just add a list of previous items
@dataclass(frozen=True, order=True)
class Phase:
    """
    Phase of the game. Each phase corresponds to a type of train.
    A Phase change occurs when a train of the matching phase is bought for the first time and change some rules of the game.
    It is important to know what the current phase of the game is, to know whether the board state is valid or not.

    Attributes:
        id(str): Same as ID of the corresponding train.
        color(Color): Highest quality Tile color that is allowed to be placed.
        limit(int): Maximum amount of Trains a Railway can have in this Phase.
        rusts(str | None): All trains with this ID will be removed from the game at the start of the phase.
    """

    id: str = field()
    color: Color = field()
    limit: int = field()
    rusts: str | None = field(default=None)

    @classmethod
    def from_json(cls, string: str) -> Phase:
        dict = json.loads(string)
        return cls.from_dict(dict)

    @classmethod
    def from_dict(cls, dict: dict) -> Phase:
        dict["color"] = Color[dict["color"]]
        return cls(**dict)
