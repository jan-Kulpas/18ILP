from __future__ import annotations
from collections import deque
import copy
from itertools import combinations, permutations
from typing import Iterable, Iterator

from core.game import Game
from core.railway import Railway
from core.settlement import City
from core.train import Train
from solver.graph import CityNode, Edge, Graph, JunctionNode, Node, Solution
from tools.exceptions import RuleError
from tools.timed import timed


class Bruteforcer:
    game: Game

    def __init__(self, game: Game) -> None:
        self.game = game

    @timed
    def solve_for(self, railway_id: str) -> Solution:
        railway = self.game.railways[railway_id]

        if not railway.floated:
            raise RuleError(
                f"Railway {railway_id} has not floated yet. (Railway is not active)"
            )
        if len(railway.trains) == 0:
            raise RuleError(f"Railway {railway_id} has no trains to find route for.")

        #railway.trains[0] = Train.from_id("D") #override for debugging
        print(f"Finding best route for {railway_id} - Trains: {railway.trains}")


        graph = Graph(self.game, railway)
        max_range: int = self._calc_max_range(railway)
        print(f"Max train range: {max_range}")

        # Setup start locations for BFS
        queue: deque[tuple[Route, Edge]] = self._init_queue(graph)
        # BFS, stopping early if at blocking city or at max train range
        routes: set[Route] = self._build_routes(graph, railway, max_range, queue)

        # Prune routes not ending at city nodes.
        routes = set(
            [route for route in routes if isinstance(route.last_stop, CityNode)]
        )

        merged_routes: set[Route] = self._merge_routes(routes, max_range)

        print(f"Routes starting at home stations: {len(routes)}")
        print(f"After adding routes going through the home station: {len(merged_routes)}")

        print(f"Train-Route pairings for {len(railway.trains)}: {sum(1 for _ in self._train_route_pairings(railway.trains, merged_routes))}")

        best_value = 0
        best_pairing = None

        for pairing in self._train_route_pairings(railway.trains, merged_routes):
            value = 0
            if Route.any_routes_share_edge([route for _, route in pairing if route]):
                continue
            for train, route in pairing:
                if route:
                    if train.diesel or (train.range and train.range >= len(route)):
                        value += sum(
                            self.game.board.settlement_at(city).revenue(train, self.game.phase)
                            for city in route.cities
                        )
            if value > best_value:
                best_value = value
                best_pairing = pairing

        nodes: dict[int, set[Node]] = {}
        edges: dict[int, set[Edge]] = {}
        cities: dict[int, set[CityNode]] = {}

        for i, tup in enumerate(best_pairing): # type: ignore
            _, route = tup
            nodes[i] = set(route.nodes if route else [])
            edges[i] = set(route.edges if route else [])
            cities[i] = set(route.cities if route else [])
        
        solution = Solution(best_value, graph, nodes, edges, cities)
        print(solution)
        return solution

    def _merge_routes(self, routes: set[Route], max_range: int) -> set[Route]:
        """
        Expands the set of routes starting in company station by joining routes at the station point,
        creating routes that go through the company station but not start there
        """
        merged = set()
        for r1, r2 in combinations(routes, 2):
            if r1.path[0] == r2.path[0]:
                r3 = Route.merge(r1, r2)
                if len(r3) <= max_range and not r3.has_subtour:
                    merged.add(r3)
        return merged

    def _calc_max_range(self, railway: Railway) -> int:
        max_range = 0
        for train in railway.trains:
            if train.diesel:
                max_range = 30
                break
            if train.range and train.range > max_range:
                max_range = train.range
        return max_range

    def _init_queue(self, graph: Graph) -> deque[tuple[Route, Edge]]:
        queue = deque()
        for home in graph.home_nodes:
            for edge in graph.incident_to(home):
                route = Route(home)
                queue.append((route, edge))

        return queue

    def _build_routes(
        self,
        graph: Graph,
        railway: Railway,
        max_range: int,
        queue: deque[tuple[Route, Edge]],
    ) -> set[Route]:
        routes = set([route for route, _ in queue])

        while queue:
            route, edge = queue.pop()
            node = edge.other(route.last_stop)

            if node not in route and len(route) < max_range:
                new_route = route.add_stop(edge, node)
                routes.add(new_route)

                if self._node_is_blocking_for(railway, node):
                    continue

                for new_edge in graph.incident_to(node):
                    if self._does_uturn(new_route, new_edge):
                        continue
                    queue.append((new_route, new_edge))

        return routes

    def _node_is_blocking_for(self, railway: Railway, node: Node):
        return (
            isinstance(node, CityNode)
            and isinstance((city := self.game.board.settlement_at(node)), City)
            and city.is_blocking_for(railway)
        )

    def _does_uturn(self, new_route: Route, new_edge: Edge):
        return (
            isinstance(new_route.last_stop, JunctionNode)
            and new_route.last_track.hex == new_edge.hex
        )

    def _train_route_pairings(
        self, trains: list[Train], routes: set[Route]
    ) -> Iterator[list[tuple[Train, Route | None]]]:
        if len(routes) < len(trains):
            raise ValueError("List B must be at least as long as list A")

        # For every number of actual elements to assign from B (0 to min(len(A), len(B)))
        for k in range(min(len(trains), len(routes)) + 1):
            # All combinations of B elements to use (choose k out of B)
            for subset in combinations(routes, k):
                # All permutations of the chosen B elements to assign them uniquely
                # Create assignment slots with 'None' to fill up remaining
                filled = list(subset) + [None] * (len(trains) - k)
                # Distribute them to A in all unique ways (because None can be repeated, use set to avoid dupes)
                for assignment in set(permutations(filled)):
                    yield list(zip(trains, assignment))


class Route:
    path: list[Node | Edge]

    def __init__(self, start: Node) -> None:
        self.path = [start]

    @classmethod
    def merge(cls, r1: Route, r2: Route) -> Route:
        if r1.path[0] != r2.path[0]:
            raise ValueError("Mismatched routes cannot be merged")
        r3 = r1.reversed()
        r3.path += r2.path[1:]
        return r3
    
    @staticmethod   
    def any_routes_share_edge(routes: list["Route"]) -> bool:
        """Return True if any two routes in the list share at least one edge."""
        for i in range(len(routes)):
            edges_i = set(routes[i].edges)
            for j in range(i + 1, len(routes)):
                if edges_i & set(routes[j].edges):  # shared edge(s) found
                    return True
        return False

    @property
    def nodes(self) -> list[Node]:
        return [item for item in self.path if isinstance(item, Node)]

    @property
    def edges(self) -> list[Edge]:
        return [item for item in self.path if isinstance(item, Edge)]

    @property
    def cities(self) -> list[CityNode]:
        return [item for item in self.path if isinstance(item, CityNode)]

    @property
    def last_stop(self) -> Node:
        return self.nodes[-1]

    @property
    def last_track(self) -> Edge:
        return self.edges[-1]

    @property
    def has_subtour(self) -> bool:
        # all parts of route should be unique if no loops
        return len(self.path) != len(set(self.path))

    def reversed(self) -> Route:
        other = copy.deepcopy(self)
        other.path.reverse()
        return other

    def add_stop(self, edge: Edge, node: Node) -> Route:
        new = copy.deepcopy(self)
        new.path += [edge, node]
        return new

    def shares_edge(self, other: Route) -> bool:
        return any((edge in other.edges) for edge in self.edges)

    def __eq__(self, other):
        if not isinstance(other, Route):
            return NotImplemented
        return hash(self) == hash(other)

    def __len__(self) -> int:
        return len([node for node in self.path if isinstance(node, CityNode)])

    def __contains__(self, item: Node | Edge):
        return item in self.path

    def __str__(self) -> str:
        s = "|"
        s += " -> ".join([str(item) for item in self.path])
        s += "|"
        return s

    def __repr__(self) -> str:
        return f"Route({str(self)})"

    def __hash__(self) -> int:
        return hash(self._canonical_path())

    def _canonical_path(self):
        s1 = tuple(str(x) for x in self.path)
        s2 = tuple(str(x) for x in reversed(self.path))
        return min(s1, s2)


if __name__ == "__main__":
    game = Game("1889")
    game.load("saves/subtour.json")

    pathfinder = Bruteforcer(game)
    pathfinder.solve_for("TR")
