from __future__ import annotations
import json
from pprint import pprint

from core.database import Database
from core.bank import Bank
from core.board import Board
from core.phase import Phase
from core.railway import Railway
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
            data = json.load(savefile)

        for railwayID, trainIDs in data["trains"].items():
            railway = self.railways[railwayID]

            railway.floated = True

            for id in trainIDs:
                train = Train.from_id(id)
                self.give_train(train, railway)

    def give_train(self, train: Train, railway: Railway):
        # TODO: drop call if train should be rusted
        if len(railway.trains) == self.phase.limit:
            raise RuleError(
                "Attempted to add a train to a railway already at train limit."
            )

        self.bank.take_train(train)
        railway.trains.append(train)

        phase = Phase.from_id(train.id)
        if phase > self.phase:
            self.change_phase(phase)

    def change_phase(self, phase: Phase):
        self.phase = phase
        # TODO: fix this
        #! jump from phase 3 to 5 skips rust event
        if phase.rusts:
            for railway in self.railways.values():
                railway.trains = [
                    train
                    for train in railway.trains
                    if train > Train.from_id(phase.rusts)
                ]


if __name__ == "__main__":
    game = Game("1889")

    game.load_save("save.json")

    print(game.phase)
    pprint(game.railways)
