from __future__ import annotations
from dataclasses import dataclass, field
import json

from core.tile import Color


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

    # ! only works cause of iffy phase ordering
    @property
    def next(self) -> Phase:
        """Returns the phase that should occur after this phase."""
        from core.database import Database

        ordered_phases = sorted(Database().phases.values())
        try:
            return ordered_phases[ordered_phases.index(self) + 1]
        except IndexError:
            raise ValueError("Tried to access next phase of the final phase")

    @property
    def prev(self) -> Phase:
        """Returns the phase that occurred before this phase."""
        from core.database import Database

        ordered_phases = sorted(Database().phases.values())
        idx = ordered_phases.index(self)
        if idx == 0:
            raise ValueError("Tried to access previous phase of the first phase")
        return ordered_phases[idx - 1]

    # ! only works cause of iffy phase ordering
    @classmethod
    def first(cls) -> Phase:
        """Returns the starting phase of the game."""

        from core.database import Database

        return min(Database().phases.values())

    @classmethod
    def from_id(cls, id: str) -> Phase:
        from core.database import Database

        return Database().phases[id]

    @classmethod
    def from_json(cls, string: str) -> Phase:
        dict = json.loads(string)
        return cls.from_dict(dict)

    @classmethod
    def from_dict(cls, dict: dict) -> Phase:
        dict["color"] = Color[dict["color"]]
        return cls(**dict)
