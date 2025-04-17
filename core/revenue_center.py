from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RevenueCenter(ABC):
    """
    Base class for revenue centers. Locations on the map that earn revenue.

    Attributes:
        value(int): Money earned for visiting the revenue center.
    """
    value: int = field(default=10)

    @classmethod
    def from_dict(cls, dict: dict) -> City | Town:
        if "size" in dict:
            return City(value=dict["value"], size=dict["size"])
        else:
            return Town(value=dict["value"])

@dataclass(frozen=True)
class Town(RevenueCenter):
    """
    A town. Revenue center which cannot hold any stations

    Attributes:
        None
    """


@dataclass(frozen=True)
class City(RevenueCenter):
    """
    A city. Revenue center which can hold a number of stations

    Attributes:
        size(int): The amount of stations that can be maximally present in the city,
    """
    size: int = field(default=1)


# Todo: Handle offboard locations
# @dataclass(frozen=True)
# class Offboard:
#    idk