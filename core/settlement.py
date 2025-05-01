from __future__ import annotations
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field

from core.enums.color import Color
from core.phase import Phase
from core.train import Train
from tools.exceptions import RuleError


@dataclass(frozen=True)
class Settlement(ABC):
    """
    Base class for revenue centers. Locations on the map that earn revenue.

    `value` is a static value of a revenue center, not every Settlement has it.
    Used for comparing which town/city is more valuable and not route calculation.

    `revenue` is a methond for calculating revenue depending on the train visiting and phase.
    Certain locations may have variable revenue based on these two things.
    Every settlement is guaranteed to implement it.
    """

    @property
    @abstractmethod
    def value(self) -> int:
        pass

    @abstractmethod
    def revenue(self, train: Train, phase: Phase) -> int:
        pass

    def build_station(self, company: str) -> None:
        raise NotImplementedError(f"{self.__class__.__name__} cannot build stations")

    @classmethod
    def from_dict(cls, dict: dict) -> Settlement:
        if "values" in dict:
            dict["values"] = {
                Color[key]: value for key, value in dict["values"].items()
            }
            return Offboard(
                **{k: dict[k] for k in ["values", "modifiers"] if k in dict}
            )
        elif "size" in dict:
            return City(value=dict["value"], size=dict["size"])
        else:
            return Town(value=dict["value"])


@dataclass(frozen=True)
class Town(Settlement):
    """
    A town. Revenue center which cannot hold any stations

    Attributes:
        value(int): Money earned for visiting the revenue center.
    """

    value: int = field(default=10)

    def revenue(self, train: Train, phase: Phase) -> int:
        return self.value


@dataclass(frozen=True)
class City(Settlement):
    """
    A city. Revenue center which can hold a number of stations

    Attributes:
        value(int): Money earned for visiting the revenue center.
        size(int): The amount of stations that can be maximally present in the city.
    """

    value: int = field(default=10)
    size: int = field(default=1)

    stations: list[str] = field(init=False, default_factory=list)

    def revenue(self, train: Train, phase: Phase) -> int:
        return self.value

    def build_station(self, company: str) -> None:
        if len(self.stations) >= self.size:
            raise RuleError("Cannot build another station because the City is full")
        self.stations.append(company)


@dataclass(frozen=True)
class Offboard(Settlement):
    values: dict[Color, int] = field()
    modifiers: dict[str, int] = field(default_factory=dict)

    # ? This may blow everything up when comparing values but it's unlikely to ever occur
    @property
    def value(self) -> int:
        raise AttributeError(
            "Offboard has a dynamic value and has to be accessed through revenue()"
        )

    # So far train overrides can be encoded in hard values
    # This needs to change for a map of maps if we ever need to do arithmetic based on both phase and train.
    def revenue(self, train: Train, phase: Phase) -> int:
        if train.id in self.modifiers:
            return self.modifiers[train.id]
        else:
            return self.values[phase.color]
