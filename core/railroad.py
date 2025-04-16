from dataclasses import dataclass, field
import json

from core.train import Train


@dataclass(frozen=True)
class Railroad:
    name: str = field()
    trains: list[Train] = field(default_factory=list, compare=False)
