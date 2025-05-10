from collections import deque

from pulp import const
from pulp import LpProblem, LpVariable, lpSum, PULP_CBC_CMD

from core.enums.direction import Direction
from core.game import Game
from core.hex import Hex
from core.railway import Railway
from core.tile import Segment
from core.train import Train
from solver.graph import CityNode, Edge, JunctionNode, Node


class Pathfinder:
    game: Game

    nodes: set[Node] = set()
    edges: set[Edge] = set()
    cities: set[CityNode] = set()
    home_nodes: set[CityNode] = set()
    trains: dict[int, Train] = {}

    def __init__(self, game: Game) -> None:
        self.game = game

        self._reset_graph()

    def _reset_graph(self) -> None:
        # Reset graph
        self.nodes: set[Node] = set()
        self.edges: set[Edge] = set()
        self.cities: set[CityNode] = set()

        self.home_nodes: set[CityNode] = set()
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

        print(len(self.edges))

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
        z = [
            LpVariable.dicts(f"z_{train}", self.nodes, cat=const.LpBinary)
            for train in self.trains
        ]  # node is terminus

        # Objective: Maximize visited city value
        problem += lpSum(
            self.game.board.settlement_at(city).revenue(
                self.trains[train], self.game.phase
            )
            * c[train][city]
            for train in self.trains
            for city in self.cities
        )

        # Constraint: cannot visit more cites than the trains range
        for train in self.trains:
            if not self.trains[train].diesel:
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

        # Constraint: Edge can only be visited if both nodes are visited.
        for train in self.trains:
            for edge in self.edges:
                node1, node2 = edge
                problem += e[train][edge] <= v[train][node1]
                problem += e[train][edge] <= v[train][node2]

        # Constraint: Visited nodes need to have 2 adjacent edges unless they're a terminal node
        for train in self.trains:
            for node in self.nodes:
                incident_edges = [edge for edge in self.edges if node in edge]
                problem += (
                    lpSum(e[train][edge] for edge in incident_edges)
                    == 2 * v[train][node] - z[train][node],
                    f"Node{node}HasTwoOrOneEdgeUsedByTrain{train}",
                )

        # Constraint: Only 2 termini nodes
        for train in self.trains:
            problem += (
                lpSum(z[train][node] for node in self.nodes) == 2,
                f"Train{train}HasOnlyTwoEnds",
            )

        # Constraint: Terminal node must be a counted city
        for train in self.trains:
            for node in self.nodes:
                if node in self.cities:
                    problem += (
                        z[train][node] <= c[train][node],
                        f"Node{node}TerminalIfCityCountedByTrain{train}",
                    )
                else:
                    problem += z[train][node] == 0

        # Constraint: Each route has to visit at least one home node
        for train in self.trains:
            problem += lpSum(c[train][home] for home in self.home_nodes) >= 1

        solver = PULP_CBC_CMD(
            msg=True,
            options=[
                "primalTolerance=1e-11",
                "integerTolerance=1e-11",
                "ratioGap=0.0",  # optional: ensure optimality
            ],
        )

        problem.solve(solver)

        used_nodes: dict[int, set[Node]] = {
            train: set(node for node in self.nodes if v[train][node].varValue == 1)
            for train in self.trains
        }
        used_edges: dict[int, set[Edge]] = {
            train: set(edge for edge in self.edges if e[train][edge].varValue == 1)
            for train in self.trains
        }
        used_cities: dict[int, set[CityNode]] = {
            train: set(city for city in self.cities if c[train][city].varValue == 1)
            for train in self.trains
        }
        used_terminals: dict[int, set[Node]] = {
            train: set(node for node in self.nodes if z[train][node].varValue == 1)
            for train in self.trains
        }
        total_value: int = sum(
            self.game.board.settlement_at(city).revenue(
                self.trains[train], self.game.phase
            )
            for city in self.cities
            for train in self.trains
            if c[train][city].varValue == 1
        )

        for train in self.trains:
            print(f"Train: {self.trains[train]}")
            print(f"Visited Nodes: {[str(n) for n in used_nodes[train]]}")
            print(f"Used Edges: {[str(e) for e in used_edges[train]]}")
            print(f"Visited Cities: {[str(c) for c in used_cities[train]]}")
            print(f"Terminal Nodes: {[str(c) for c in used_terminals[train]]}")

        print(f"Total Value: {total_value}")

        print(
            {
                train: [z[train][city].varValue for city in self.nodes]
                for train in self.trains
            }
        )

        return total_value, used_nodes, used_edges, used_cities

    def _build_graph(self, railway: Railway) -> None:
        self._reset_graph()

        self.trains = {idx: train for idx, train in enumerate(railway.trains)}
        self.home_nodes = set(self._get_station_segment_nodes(railway))

        queue: deque[Node] = deque(self.home_nodes)

        while queue:
            node = queue.popleft()

            if node in self.nodes:
                continue  # Skip already visited

            self.nodes.add(node)

            match node:
                case CityNode():
                    self._process_city(node, queue)
                case JunctionNode():
                    self._process_junction(node, queue)

    def _get_station_segment_nodes(self, railway: Railway) -> list[CityNode]:
        # The nullcheck takes care of None type
        return [
            CityNode(hex, tile.get_station_location(railway))  # type: ignore
            for hex, tile in self.game.board.items()
            if tile.has_station(railway)
        ]

    def _process_city(self, node: CityNode, queue: deque[Node]) -> None:
        print(f"Visiting city: {node}")
        self.cities.add(node)

        hex = node.hex

        # TODO: check if blocked

        # Add outgoing edge to every junction and queue that junction
        for direction in self.game.board.segment_at(node).tracks:
            neighbour = hex.neighbour(direction)
            junction = JunctionNode((hex, neighbour))
            queue.append(junction)
            self.edges.add(Edge((node, junction)))

    def _process_junction(self, node: JunctionNode, queue: deque[Node]) -> None:
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
        from_hex, to_hex = node.hexes

        # Get the actual segments that are connected to the junction
        # Pair segment and hex for city id (not converting we need to handle None case)
        cities: list[tuple[Hex, Segment]] = get_connected_segments(
            from_hex, to_hex
        ) + get_connected_segments(to_hex, from_hex)

        # Go through every neighbouring thing and add edge to list and thing to queue
        for hex, seg in cities:
            if seg.location:
                city = CityNode(hex, seg.location)
                queue.append(city)
                self.edges.add(Edge((node, city)))
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
                    junction = JunctionNode((hex, neighbour))
                    queue.append(junction)
                    self.edges.add(Edge((node, junction)))


if __name__ == "__main__":
    game = Game("1889")
    game.load_save("save.json")

    pathfinder = Pathfinder(game)
    pathfinder.solve_for("UR")

    print()
