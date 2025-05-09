from pprint import pprint
from pulp import LpProblem, LpVariable, lpSum
from pulp import const

from core.enums.direction import Direction
from core.enums.settlement_location import SettlementLocation
from core.game import Game
from core.hex import Hex
from core.railway import Railway

from collections import deque

from core.tile import Segment
from core.train import Train


class Pathfinder:
    game: Game

    nodes: set[str] = set()
    edges: set[tuple[str, str]] = set()
    cities: set[str] = set()

    def __init__(self, game: Game) -> None:
        self.game = game

        self._reset_graph()

    def _reset_graph(self) -> None:
        # Reset graph
        self.nodes: set[str] = set()
        self.edges: set[tuple[str, str]] = set()
        self.cities: set[str] = set()
        self.trains: dict[int, Train] = {}

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

        self._build_graph(railway)

        problem = LpProblem("MaximalRouteFinding", const.LpMaximize)

        v = [
            LpVariable.dicts(f"v_{train}", self.nodes, cat=const.LpBinary)
            for train in self.trains
        ]  # vertex visited
        e = [
            LpVariable.dicts(f"e_{train}", self.edges, cat=const.LpBinary)
            for train in self.trains
        ]  # edge visited
        c = [
            LpVariable.dicts(f"c_{train}", self.cities, cat=const.LpBinary)
            for train in self.trains
        ]  # city counted

        # Objective: Maximize visited city value
        problem += lpSum(
            self.game.board.settlement_at(city).revenue(
                self.trains[train], self.game.phase
            )
            * c[train][city]
            for train in self.trains
            for city in self.cities
        )

        # TODO: if check for diesels to disable
        # Constraint: cannot visit more cites than the trains range
        for train in self.trains:
            problem += (
                lpSum(c[train][city] for city in self.cities)
                <= self.trains[train].range,
                f"Train{train}MaxCitiesVisited",
            )

        # Constraint: Trains can only score cities they pass through
        for train in self.trains:
            for city in self.cities:
                problem += (
                    c[train][city] == v[train][city],
                    f"City{city}CountedIfVisitedByTrain{train}",
                )

        # Constraint: Trains cannot pass through edge another train has already used
        for edge in self.edges:
            problem += (
                lpSum(e[train][edge] for train in self.trains) <= 1,
                f"Edge{edge}UsedOnce",
            )

        # Constraint: Visited nodes need at least one incident edge
        for train in self.trains:
            for node in self.nodes:
                incident_edges = [edge for edge in self.edges if node in edge]
                problem += (
                    lpSum(e[train][edge] for edge in incident_edges) >= v[train][node],
                    f"Node{node}HasUsedEdgeByTrain{train}",
                )

        problem.solve()

        for train in self.trains:
            print(
                "Visited Nodes:",
                [node for node in self.nodes if v[train][node].varValue == 1],
            )
            print(
                "Used Edges:",
                [edge for edge in self.edges if e[train][edge].varValue == 1],
            )
            print(
                "Visited Cities:",
                [city for city in self.cities if c[train][city].varValue == 1],
            )

        print(
            "Total Value:",
            sum(
                self.game.board.settlement_at(city).revenue(
                    self.trains[train], self.game.phase
                )
                for city in self.cities
                for train in self.trains
                if c[train][city].varValue == 1
            ),
        )

    def _build_graph(self, railway: Railway) -> None:
        self._reset_graph()

        self.trains = {idx: train for idx, train in enumerate(railway.trains)}

        queue: deque[tuple[str, str]] = deque(
            [(id, "city") for id in self._get_station_segment_ids(railway)]
        )

        while queue:
            node, kind = queue.popleft()

            if node in self.nodes:
                continue  # Skip already visited

            self.nodes.add(node)

            match kind:
                case "city":
                    self._process_city(node, queue)
                case "junction":
                    self._process_junction(node, queue)

    def _get_station_segment_ids(self, railway: Railway) -> list[str]:
        # The nullcheck takes care of None type
        return [
            self.city_name(hex, tile.get_station_location(railway))  # type: ignore
            for hex, tile in self.game.board.items()
            if tile.has_station(railway)
        ]

    def _process_city(self, node: str, queue: deque[tuple[str, str]]) -> None:
        print(f"Visiting city: {node}")
        self.cities.add(node)

        hex = Hex.from_string(node.split(".")[0])

        # TODO: check if blocked

        # Add outgoing edge to every junction and queue that junction
        for direction in self.game.board.segment_at(node).tracks:
            neighbour = hex.neighbour(direction)
            junction = self.junction_name(hex, neighbour)

            self.edges.add((node, junction))
            queue.append((junction, "junction"))

    def _process_junction(self, node: str, queue: deque[tuple[str, str]]) -> None:
        print(f"Visiting junction: {node}")

        def get_connected_segments(
            base_hex: Hex, other_hex: Hex
        ) -> list[tuple[Hex, Segment]]:
            direction = Direction.from_unit_hex(other_hex - base_hex)
            return [
                (base_hex, seg)
                for seg in self.game.board[base_hex].segments_with_exit(direction)
            ]

        # Get the Hexes neighbouring with the junction
        hexes = [Hex.from_string(coord) for coord in node.split("-")]
        from_hex, to_hex = hexes

        # Get the actual segments that are connected to the junction
        # Pair segment and hex for city id (not converting we need to handle None case)
        cities: list[tuple[Hex, Segment]] = get_connected_segments(
            from_hex, to_hex
        ) + get_connected_segments(to_hex, from_hex)

        # Go through every neighbouring thing and add edge to list and thing to queue
        for hex, seg in cities:
            if seg.location:
                city = f"{hex}.{seg.location.name}"
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
                    junction = self.junction_name(hex, neighbour)
                    queue.append((junction, "junction"))
                    self.edges.add((node, junction))

    def city_name(self, h: Hex, l: SettlementLocation) -> str:
        return f"{h}.{l.name}"

    def junction_name(self, h1: Hex, h2: Hex) -> str:
        return f"{h1}-{h2}" if str(h1) < str(h2) else f"{h2}-{h1}"


if __name__ == "__main__":
    game = Game("1889")
    game.load_save("save.json")

    pathfinder = Pathfinder(game)
    pathfinder.solve_for("UR")
