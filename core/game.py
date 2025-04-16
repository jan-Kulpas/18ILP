from core.database import Database
from core.manifest import Manifest
from core.board import Board
from core.railway import Railway
from core.train import Phase


class Game:
    def __init__(self, year: str) -> None:
        self.year = year
        self.database = Database(year)

        self.manifest = Manifest(year)
        self.board = Board(year)
        self.railways: list[Railway] = self.board.load_railways()
        self.phase = "0"


if __name__ == "__main__":
    game = Game("1889")
    print(game.database.phases)
    print(game.railways)

    p = game.database.phases

    print(p["5"] < p["6"])

    print(game.database.trains)
