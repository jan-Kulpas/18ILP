from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from core.phase import Phase
from core.train import Train


@dataclass(frozen=True)
class Settlement(ABC):
    """
    Base class for revenue centers. Locations on the map that earn revenue.

    Attributes:
        value(int): Money earned for visiting the revenue center.
    """
    @property
    @abstractmethod
    def value(self) -> int:
        pass

    @abstractmethod
    def revenue(self, train: Train, phase: Phase) -> int:
        pass

    @classmethod
    def from_dict(cls, dict: dict) -> City | Town:
        if "size" in dict:
            return City(value=dict["value"], size=dict["size"])
        else:
            return Town(value=dict["value"])

@dataclass(frozen=True)
class Town(Settlement):
    """
    A town. Revenue center which cannot hold any stations

    Attributes:
        None
    """
    value: int = field(default=10)

    def revenue(self, train: Train, phase: Phase) -> int:
        return self.value
        

@dataclass(frozen=True)
class City(Settlement):
    """
    A city. Revenue center which can hold a number of stations

    Attributes:
        size(int): The amount of stations that can be maximally present in the city,
    """
    value: int = field(default=10)
    size: int = field(default=1)

    def revenue(self, train: Train, phase: Phase) -> int:
        return self.value


# Todo: Handle offboard locations
@dataclass(frozen=True)
class Offboard(Settlement):
   # ? This may blow everything up when comparing values but it's unlikely to ever occur
   @property
   def value(self) -> int:
       raise AttributeError("Offboard has a dynamic value and has to be accessed through revenue()")
   
   def revenue(self, train: Train, phase: Phase) -> int:
       raise NotImplementedError()