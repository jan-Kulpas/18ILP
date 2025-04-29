from __future__ import annotations
from abc import ABC
import json

from enum import Enum, Flag
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any

from core.settlement import City, Settlement, Town

class Direction(Enum):
    """
    Direction in which a track may go, i.e. edges of a hex or revenue centers located on it.
    """
    N = 0
    NE = 1
    SE = 2
    S = 3
    SW = 4
    NW = 5

    def rotated(self, r: int) -> Direction:
        return Direction((self.value + r) % len(Direction))

class SettlementLocation(Enum):
    C = 0 # Center for Lawsonian tiles
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6

    def rotated(self, r: int) -> SettlementLocation:
        if self == SettlementLocation.C:
            return self
        else:
            value = ((self.value - 1) + r) % (len(SettlementLocation) - 1) + 1
            return SettlementLocation(value)

class Color(Flag):
    """
    Tile color, can be combined bitwise to represent multiple colors
    """

    BLANK = 0
    YELLOW = 1
    GREEN = 2
    BROWN = 4
    GRAY = 8
    RED = 16

# TODO: Maybe handle both tracks and settlements to handle city, and cityless cases? (awful)
@dataclass(frozen=True)
class Segment:
    tracks: list[Direction] = field(default_factory=list)
    settlement: Settlement | None = field(default=None)
    location: SettlementLocation | None = field(default=None)
    
    @classmethod
    def from_json(cls, string: str) -> Segment:
        dict = json.loads(string)
        return Segment.from_dict(dict)
    
    @classmethod
    def from_dict(cls, dict: dict) -> Segment:
        if "tracks" in dict:
            dict["tracks"] = [Direction[dir] for dir in dict["tracks"]]
        if "settlement" in dict:
            dict["settlement"] = Settlement.from_dict(dict["settlement"])
        if "location" in dict:
            dict["location"] = SettlementLocation[dict["location"]]
        
        return Segment(**dict)
    
    def rotated(self, r: int) -> Segment:
        return Segment(
            [dir.rotated(r) for dir in self.tracks],
            self.settlement,
            self.location.rotated(r) if self.location else None
        )

@dataclass(eq=True, frozen=True)
class Tile:
    """
    A single tile that can be placed on the board.

    Note that this doesn't contain info on the position on board but the contents of the tile.

    The tile rotation is also included as the rotated method changes every track direction in the tile so it encodes that anyway

    Attributes:
        id (str): ID printed on the tile.
        tracks (list[tuple[Direction, Direction]]): List of track segments made of a tuple containing the 2 endpoints of a curve.
        color (Color): Color of the tile, can be multiple colors using bitwise operations
        cities (list[RevenueCenter]): List of revenue centers printed on the tile.
        label (str): Alpha code printed on the tile.
        upgrades (list[str]): List of tile IDs that this tile could be upgraded to.
    """

    id: str = field()
    color: Color = field()
    segments: list[Segment] = field(default_factory=list)
    label: str | None = field(default=None, compare=False)
    upgrades: list[str] = field(default_factory=list, compare=False)
    rotation: int = field(default=0)

    @classmethod
    def blank(cls) -> Tile:
        return cls("0", Color.BLANK, upgrades=["7", "8", "9"])

    @classmethod
    def from_id(cls, id: str) -> Tile:
        from core.database import Database

        return Database().tiles[id]

    @classmethod
    def from_json(cls, string: str) -> Tile:
        dict = json.loads(string)
        return Tile.from_dict(dict)
    
    @classmethod
    def from_dict(cls, dict: dict) -> Tile:
        if "cities" in dict:
            dict["cities"] = [Settlement.from_dict(city_dict) for city_dict in dict["cities"]]
        if "segments" in dict:
            dict["segments"] = [Segment.from_dict(segment) for segment in dict["segments"]]
        
        return Tile(
            id=dict["id"],
            color=Color(sum([Color[name].value for name in dict["color"]])),
            **{k: dict[k] for k in ["segments", "label", "upgrades"] if k in dict},
        )
    
    @property
    def json(self):
        return json.dumps(self, cls=_TileEncoder)
    
    def rotated(self, r: int) -> Tile:
        return Tile(
            self.id,
            self.color,
            [segment.rotated(r) for segment in self.segments],
            self.label,
            self.upgrades,
            (self.rotation + r) % 6
        )
    
    def is_upgrade(self, other: Tile) -> bool:
        """
        Returns True if this tile is a direct upgrade of the `other` tile.
        """
        return self.id in other.upgrades

    def preserves_track(self, other: Tile) -> bool:
        """
        Returns True if every segment in `other` can be assigned to a distinct
        segment in self whose tracks ⊇ the other's tracks.
        """
        
        # Convert segments into track sets to easily check if one contains the other
        other_sets = [set(seg.tracks) for seg in other.segments if seg.tracks]
        self_sets  = [set(seg.tracks) for seg in self.segments  if seg.tracks]

        # Fail if the other segment list is too big to match 1:1 with self segments
        if len(other_sets) > len(self_sets):
            return False

        # For tracking which segments have been mapped
        used = [False] * len(self_sets)

        # Try to map other_sets to self_sets, mark as used of if matched
        # Then, recusively try to match rest of the list, unmark as used if recursive match failed.
        def match(idx: int) -> bool:
            # all other segments have been matched
            if idx == len(other_sets):
                return True

            needed = other_sets[idx]
            for j, available in enumerate(self_sets):
                if not used[j] and needed.issubset(available):
                    used[j] = True
                    if match(idx + 1):
                        return True
                    used[j] = False

            return False

        return match(0)

    def preserves_settlements(self, other: Tile) -> bool:
        """
        Returns True iff `self` preserves all settlements from `other`:
          - exact same locations
          - settlement values in `self` >= those in `other`
          - for cities, sizes in `self` >= those in `other`
        """
        other_map = {
            seg.location: seg.settlement
            for seg in other.segments
            if seg.settlement is not None
        }
        self_map = {
            seg.location: seg.settlement
            for seg in self.segments
            if seg.settlement is not None
        }

        # No new location and no removed locations
        if self_map.keys() != other_map.keys():
            return False

        for loc, old_settlement in other_map.items():
            new_settlement = self_map[loc]
            
            # value >= other.value
            if new_settlement.value < old_settlement.value:
                return False

            # If both are city: size >= other.size
            if isinstance(old_settlement, City):
                if not isinstance(new_settlement, City):
                    return False
                if new_settlement.size < old_settlement.size:
                    return False

        return True


class _TileEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Color):
            flags = []
            for flag in obj:
                flags.append(flag.name)
            if not flags:
                return [Color.BLANK.name]
            return flags
        elif isinstance(obj, Enum):
            return obj.name
        elif is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)
        elif isinstance(obj, tuple):
            return list(obj)
        return super().default(obj)