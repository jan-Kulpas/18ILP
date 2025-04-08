from tile import *
from game import *
from tile_manifest import TileManifest, TILES

if __name__ == "__main__":
    game = Game("1889")

    print(game.manifest)
    print(hash(TILES["9"]))
    
