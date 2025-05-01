from __future__ import annotations
import copy
from dataclasses import dataclass, field
import json


# ! order=True compares the ID which just happens to work for 1889 but may not for others!
@dataclass(frozen=True, order=True)
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
    def from_id(cls, id: str) -> Train:
        from core.database import Database

        return copy.deepcopy(Database().trains[id])

    @classmethod
    def from_json(cls, string: str) -> Train:
        dict = json.loads(string)
        return Train.from_dict(dict)

    @classmethod
    def from_dict(cls, dict: dict) -> Train:
        keys = ["id", "range", "diesel"]
        return Train(**{k: dict[k] for k in keys if k in dict})
