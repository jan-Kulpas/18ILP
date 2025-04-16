from __future__ import annotations
from dataclasses import dataclass, field
import json
from typing import Any


@dataclass(frozen=True)
class Train:
    id: str = field()
    # ? Consider using a property for range calculation
    range: int | None = field(default=None)

    # Powers
    diesel: bool = field(default=False)

    @classmethod
    def from_json(cls, string: str) -> Train:
        return json.loads(string, object_hook=_decode_train)

    @classmethod
    def from_dict(cls, dict: dict) -> Train:
        return cls.from_json(json.dumps(dict))

    # TODO: Implement to_json() when needed
    # @property
    # def json(self):
    #     pass


def _decode_train(dct: dict) -> Any:
    if "id" in dct:
        keys = ["id", "range", "diesel"]
        return Train(**{k: dct[k] for k in keys if k in dct})
