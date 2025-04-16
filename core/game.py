from core.database import Database
from core.manifest import Manifest
from core.board import Board


class Game:
    def __init__(self, year: str) -> None:
        self.year = year
        self.manifest = Manifest(year)
        self.database = Database(year)
        self.board = Board(year)


if __name__ == "__main__":
    game = Game("1889")
    print(game.manifest)
    print(game.database)
