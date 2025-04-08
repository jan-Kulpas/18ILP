from tile_manifest import TileManifest

class Game:
    def __init__(self, year: str) -> None:
        self.year = year
        self.manifest = TileManifest(year)