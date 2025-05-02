from __future__ import annotations
import json
from pprint import pprint

from core.database import Database
from core.bank import Bank
from core.board import Board
from core.enums.settlement_location import SettlementLocation
from core.hex import Hex
from core.phase import Phase
from core.railway import Railway
from core.settlement import Town, Offboard, City
from core.tile import Tile
from core.train import Train
from tools.exceptions import RuleError


class Game:
    def __init__(self, year: str) -> None:
        self.year = year

        # Init database singleton
        self.database = Database(year)

        self.bank: Bank = Bank(year)
        self.board: Board = Board(year)
        self.railways: dict[str, Railway] = self.board.load_railways()
        self.phase: Phase = Phase.first()

    def load_save(self, path: str) -> None:
        with open(path) as savefile:
            savedata = json.load(savefile)

        # Load trains and railways
        for railwayID, trainIDs in savedata["trains"].items():
            railway = self.railways[railwayID]

            railway.floated = True

            for id in trainIDs:
                train = Train.from_id(id)
                self.give_train(train, railway)

        # Update board
        for coord, data in savedata["board"].items():
            hex = Hex.from_string(coord)
            tile = Tile.from_id(data["tile"]).rotated(data["rotation"])

            self.place_tile(hex, tile)

        # TODO: Add ability to read which city is the station on if multiple.
        # Place stations
        for coord, railways in savedata["stations"].items():
            hex = Hex.from_string(coord)
            for id in railways:
                self.place_station(hex, self.railways[id])

    def place_tile(self, hex: Hex, tile: Tile):
        board_tile = self.board[hex]

        if tile.color.value > self.phase.color.value:
            raise RuleError(
                f"Cannot place Tile at {hex} because its color ({tile.color}) is higher the current phase ({self.phase.color})"
            )
        # MAYBE: check whether tile extends track or improves a settlement instead of merely preserving it
        if not tile.preserves_track(board_tile):
            raise RuleError(
                f"Cannot place Tile at {hex} because it ({tile.id}) does not preserve track of previous tile ({board_tile.id})."
            )
        if not tile.preserves_settlements(board_tile):
            raise RuleError(
                f"Cannot place Tile at {hex} because it ({tile.id}) does not upgrade any of the settlements of previous tile ({board_tile.id})."
            )
        if not tile.label == board_tile.label:
            raise RuleError(
                f"Cannot place Tile at {hex} because its ({tile.id}) label does not match that of the previous tile ({board_tile.id})."
            )
        # TODO: Check for going outside map with an edge

        # MAYBE: Change save board structure from map to list if storing previous tiles becomes important
        # ? This may contain settlement preserving in itself
        # ! Can't check for direct upgrade during loading save data as we don't store the previous tile state
        # if (not new_tile.is_upgrade(board_tile)):
        #     raise RuleError(f"Cannot place the new tile since it is not an upgrade of the previous tile")

        self.board[hex] = tile

    def give_train(self, train: Train, railway: Railway):
        """
        Adds a train to a railway.

        Raises:
            RuleError: Attempted to add a train to a railway already at train limit.
            RuleError: There are no more copies of this train in the Bank.
        """
        if len(railway.trains) == self.phase.limit:
            raise RuleError(
                "Attempted to add a train to a railway already at train limit."
            )

        self.bank.take_train(train)
        railway.trains.append(train)

        phase = Phase.from_id(train.id)
        if phase > self.phase:
            self.change_phase(phase)

    def place_station(
        self,
        hex: Hex,
        railway: Railway,
        location: SettlementLocation = SettlementLocation.C,
    ) -> None:
        """
        Places a station token of a given railway on the given tile.

        There's an optional location argument that has to be specified if the tile has multiple cities
        """
        # TODO: Check for station with a spot reserved for unfloated railways
        tile = self.board[hex]

        # Get the correct city from the tile
        city = next(
            (seg.settlement for seg in tile.segments if seg.location == location), None
        )

        if not city:
            raise ValueError("Tried to place a station in a non existent city.")
        if not railway.stations > 0:
            raise RuleError("Railway doesn't have any stations left.")

        # Update railway and start it if it's not floated yet
        railway.stations -= 1
        railway.floated = True

        city.build_station(railway.id)

    def change_phase(self, new_phase: Phase):
        """Sets current phase to given phase and enforces train rusting and train limits."""
        # Reccurently change phase to all in-between phases
        # so that we don't miss any rust event
        if self.phase != new_phase.prev:
            self.change_phase(new_phase.prev)

        self.phase = new_phase

        # Rust trains
        if new_phase.rusts:
            # Clear bank
            self.bank.trains[new_phase.rusts] = 0
            # Clear railways
            for railway in self.railways.values():
                railway.trains = [
                    train
                    for train in railway.trains
                    if train > Train.from_id(new_phase.rusts)
                ]
        # Remove trains above limit (in case rust event was not enough)
        for railway in self.railways.values():
            if len(railway.trains) > self.phase.limit:
                railway.trains = list(reversed(sorted(railway.trains)))
                railway.trains = railway.trains[: self.phase.limit]


if __name__ == "__main__":
    game = Game("1889")

    # print(Tile.from_id("23").preserves_track(Tile.from_id("8").rotated(4)))

    game.load_save("save.json")
