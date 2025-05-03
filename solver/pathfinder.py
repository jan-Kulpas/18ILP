from pprint import pprint
from pulp import LpProblem
from pulp import const

from core.enums.direction import Direction
from core.enums.settlement_location import SettlementLocation
from core.game import Game
from core.hex import Hex
from core.railway import Railway

from collections import deque

from core.tile import Segment


class Pathfinder:
    game: Game

    nodes: set[str] = set()
    edges: set[tuple[str, str]] = set()

    def __init__(self, game: Game) -> None:
        self.game = game

        self.nodes: set[str] = set()
        self.edges: set[tuple[str, str]] = set()

    # TODO: figure out return type.
    def solve_for(self, railway_id: str):
        railway = self.game.railways[railway_id]

        if not railway.floated:
            raise ValueError(
                f"Railway {railway_id} has not floated yet. (Railway is not active)"
            )
        if len(railway.trains) == 0:
            raise ValueError(f"Railway {railway_id} has no trains to find route for.")

        print(f"Finding best route for {railway_id} - Trains: {railway.trains}")

        self.build_graph(railway)

        problem = LpProblem("MaximalRouteFinding", const.LpMaximize)

    def build_graph(self, railway: Railway) -> None:
        # The nullcheck takes care of None type
        home_hexes: list[tuple[Hex, SettlementLocation]] = [
            (hex, tile.get_station_location(railway))
            for hex, tile in self.game.board.items()
            if tile.has_station(railway)
        ]  # type: ignore

        queue: deque[tuple[str, str]] = deque(
            [(f"{hex}.{loc.name}", "city") for hex, loc in home_hexes]
        )

        # Reset graph
        self.nodes: set[str] = set()
        self.edges: set[tuple[str, str]] = set()

        while queue:
            node, kind = queue.popleft()

            match kind:
                case "city":
                    print(f"Visiting city: {node}")
                    self.nodes.add(node)  # mark visited
                    hex = Hex.from_string(node.split(".")[0])

                    # TODO: check if blocked

                    # Add outgoing edge to every junction and queue that junction
                    for dir in self.game.board.segment_at(node).tracks:
                        neighbour = hex.neighbour(dir)
                        junction = f"{hex}-{neighbour}" if str(hex) < str(neighbour) else f"{neighbour}-{hex}"

                        if junction not in self.nodes:
                            queue.append((junction, "junction"))
                        self.edges.add((node, junction))

                case "junction":
                    print(f"Visiting junction: {node}")
                    self.nodes.add(node)

                    # Get the Hexes neighbouring with the junction
                    hexes = [Hex.from_string(coord) for coord in node.split("-")]
                    from_hex = hexes[0]
                    to_hex = hexes[1]

                    # Get the actual segments that are connected to the junction
                    from_segments: list[Segment] = self.game.board[
                        from_hex
                    ].segments_with_exit(Direction.from_unit_hex(to_hex - from_hex))
                    to_segments: list[Segment] = self.game.board[
                        to_hex
                    ].segments_with_exit(Direction.from_unit_hex(from_hex - to_hex))

                    # Pair segment and hex for city id (not converting we need to handle None case)
                    cities: list[tuple[Hex, Segment]] = []
                    cities += [(from_hex, seg) for seg in from_segments]
                    cities += [(to_hex, seg) for seg in to_segments]

                    # Go through every neighbouring thing and add edge to list and thing to queue
                    for hex, seg in cities:
                        if seg.location:
                            city = f"{hex}.{seg.location.name}"
                            if city not in self.nodes:
                                queue.append((city, "city"))
                            self.edges.add((node, city))
                        else:
                            # Oops! There's no city actually so we need to make an edge to the next junction.
                            # I am not sure if there can be multiple directions but just in case.
                            directions = [
                                dir
                                for dir in seg.tracks
                                if hex.neighbour(dir) not in [from_hex, to_hex]
                            ]
                            for dir in directions:
                                neighbour = hex.neighbour(dir)
                                junction = f"{hex}-{neighbour}" if str(hex) < str(neighbour) else f"{neighbour}-{hex}"
                                if junction not in self.nodes:
                                    queue.append((junction, "junction"))
                                self.edges.add((node, junction))


if __name__ == "__main__":
    game = Game("1889")
    game.load_save("save.json")

    pathfinder = Pathfinder(game)
    pathfinder.solve_for("UR")
