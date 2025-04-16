from __future__ import annotations
from dataclasses import dataclass, field
import json

from core.hex import Hex
from core.train import Train


@dataclass(frozen=True)
class Railway:
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
