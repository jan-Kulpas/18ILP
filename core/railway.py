from __future__ import annotations
from dataclasses import dataclass, field
import json

from core.hex import Hex
from core.train import Train


@dataclass()
class Railway:
    """
    A player entity. Collects trains and runs them during their turn.

    The maximum possible revenue from a given train depends on which Railway
    it belongs to as that influences which stations are passable.

    Attributes:
        name(str): ID of the Railway.
        home(Hex): Coordinates of the city/town that will contain the first station when it gets floated.
        trains(list[Train]): List of Trains belonging to this Railway.
        floated(bool): Whether the railway is active or not.
    """

    name: str = field()
    home: Hex = field()
    trains: list[Train] = field(default_factory=list, compare=False)
    floated: bool = field(default=False)

    @classmethod
    def from_json(cls, string: str) -> Railway:
        dict = json.loads(string)
        return cls.from_dict(dict)

    @classmethod
    def from_dict(cls, dict: dict) -> Railway:
        dict["home"] = Hex.from_string(dict["home"])
        return cls(**dict)
