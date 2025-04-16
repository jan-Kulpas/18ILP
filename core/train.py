from __future__ import annotations
from dataclasses import dataclass, field
import json

from core.tile import Color


@dataclass(frozen=True)
class Train:
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

    # TODO: Implement to_json() when needed
    # @property
    # def json(self):
    #     pass


# ! order=True compares the ID which just happens to work for 1889 but may not for others!
# ? consider adding a postinit field that would be a counter of added phases and compare based on that
# ? or just add a list of previous items
@dataclass(frozen=True, order=True)
class Phase:
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
