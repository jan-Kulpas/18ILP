from __future__ import annotations
import json
from pprint import pprint

from core.database import Database
from core.bank import Bank
from core.board import Board
from core.hex import Hex
from core.phase import Phase
from core.railway import Railway
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
            tile = Tile.from_id(data["tile"])
            rotation = data["rotation"]

            self.place_tile(hex, tile, rotation)

    def place_tile(self, hex: Hex, tile: Tile, rotation: int):
        # TODO: Handle rotation
        # TODO: Handle phase validation
        # TODO: Handle city/label validation
        # TODO: Handle edge validation
        self.board[hex].tile = tile

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

    game.load_save("save.json")

    print(game.phase)
    pprint(game.railways)
    print(game.bank.trains)
