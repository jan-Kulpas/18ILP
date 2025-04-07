from tile import *

if __name__ == "__main__":
    tile = Tile(
        id="9",
        tracks=[(Direction.N, Direction.S), (Direction.R1, Direction.SE)],
        color=Color.YELLOW | Color.GREEN,
        cities=[City(value=2, size=2), Town()],
        label="X",
        upgrades=["3", "5", "A2"],
    )

    print(tile)
    print(tile.json)
    tile2 = Tile.from_json(tile.json)
    print(tile2)
