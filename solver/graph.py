from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field

from core.enums.direction import Direction
from core.enums.settlement_location import SettlementLocation
from core.game import Game
from core.hex import Hex
from core.railway import Railway
from core.settlement import City
from core.tile import Segment
from core.train import Train


class Node(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def is_on_hex(self, hex: Hex) -> bool:
        pass


@dataclass(frozen=True, eq=True)
class CityNode(Node):
    hex: Hex = field()
    loc: SettlementLocation = field()

    def __str__(self) -> str:
        return f"{self.hex}.{self.loc.name}"

    def is_on_hex(self, hex: Hex) -> bool:
        return hex == self.hex


@dataclass(frozen=True, eq=True)
class JunctionNode(Node):
    hexes: tuple[Hex, Hex] = field()

    def __post_init__(self):
        if str(self.hexes[0]) > str(self.hexes[1]):
            object.__setattr__(self, "hexes", (self.hexes[1], self.hexes[0]))

    def __iter__(self):
        return iter(self.hexes)

    def __str__(self) -> str:
        return f"{self.hexes[0]}-{self.hexes[1]}"

    def is_on_hex(self, hex: Hex) -> bool:
        return hex in self.hexes


@dataclass(frozen=True, eq=True)
class Edge:
    nodes: tuple[Node, Node] = field()
    hex: Hex = field()

    def __post_init__(self):
        if str(self.nodes[0]) > str(self.nodes[1]):
            object.__setattr__(self, "nodes", (self.nodes[1], self.nodes[0]))

    def other(self, node: Node) -> Node:
        if node == self.nodes[0]:
            return self.nodes[1]
        if node == self.nodes[1]:
            return self.nodes[0]
        raise ValueError(f"Node {node} is not part of Edge {self}")

    def __iter__(self):
        return iter(self.nodes)

    def __str__(self) -> str:
        return f"({self.nodes[0]}, {self.nodes[1]})"


class Graph:
    game: Game

    nodes: set[Node] = set()
    edges: set[Edge] = set()
    cities: set[CityNode] = set()
    home_nodes: set[CityNode] = set()

    trains: dict[int, Train] = {}

    def __init__(self, game: Game, railway: Railway) -> None:
        self.game = game
        self.nodes: set[Node] = set()
        self.edges: set[Edge] = set()
        self.cities: set[CityNode] = set()

        self.trains = {idx: train for idx, train in enumerate(railway.trains)}
        self.home_nodes = set(self._get_station_segment_nodes(railway))
        self.railway: Railway = railway

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

    def incident_to(self, node: Node) -> set[Edge]:
        return set([edge for edge in self.edges if node in edge])

    def _get_station_segment_nodes(self, railway: Railway) -> list[CityNode]:
        # The nullcheck takes care of None type
        return [
            CityNode(hex, tile.get_station_location(railway))  # type: ignore
            for hex, tile in self.game.board.items()
            if tile.has_station(railway)
        ]

    def _process_city(self, node: CityNode, queue: deque[Node]) -> None:
        # print(f"Visiting city: {node}")
        self.cities.add(node)

        # Abort if blocked, can't pass through
        match city := self.game.board.settlement_at(node):
            case City():
                if city.is_blocking_for(self.railway):
                    return

        hex = node.hex
        # Add outgoing edge to every junction and queue that junction
        for direction in self.game.board.segment_at(node).tracks:
            neighbour = hex.neighbour(direction)
            junction = JunctionNode((hex, neighbour))
            queue.append(junction)
            self.edges.add(Edge((node, junction), hex))

    def _process_junction(self, node: JunctionNode, queue: deque[Node]) -> None:
        # print(f"Visiting junction: {node}")
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
                self.edges.add(Edge((node, city), hex))
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
                    self.edges.add(Edge((node, junction), hex))


class Solution:
    nodes: dict[int, set[Node]]
    edges: dict[int, set[Edge]]
    cities: dict[int, set[CityNode]]

    value: int
    graph: Graph

    def __init__(self, value: int, graph: Graph, nodes, edges, cities) -> None:
        self.value = value
        self.graph = graph
        self.nodes = nodes
        self.edges = edges
        self.cities = cities

    @classmethod
    def from_ilp(cls, graph: Graph, a, v, e, c) -> Solution:
        nodes = {
            train: set(node for node in graph.nodes if v[train][node].varValue == 1)
            for train in graph.trains
        }
        edges = {
            train: set(edge for edge in graph.edges if e[train][edge].varValue == 1)
            for train in graph.trains
        }
        cities = {
            train: set(city for city in graph.cities if c[train][city].varValue == 1)
            for train in graph.trains
        }

        value = sum(
            graph.game.board.settlement_at(city).revenue(
                graph.trains[train], graph.game.phase
            )
            for city in graph.cities
            for train in graph.trains
            if c[train][city].varValue == 1
        )

        return Solution(value, graph, nodes, edges, cities)
    
    @classmethod
    def from_unsolved_graph(cls, graph: Graph) -> Solution:
        return Solution(0, graph, {0:graph.nodes}, {0:graph.edges}, {0:graph.cities})

    @property
    def trains_with_subtour(self) -> dict[int, Train]:
        return {
            idx: train
            for idx, train in self.graph.trains.items()
            if self.has_subtour_at(idx)
        }

    def has_subtour_at(self, idx: int) -> bool:
        nodes = self.nodes[idx]
        edges = self.edges[idx]

        if len(nodes) == 0 or len(edges) == 0:
            return False

        visited: set[Node] = set()
        adjacency = {}
        for edge in edges:
            u, v = edge.nodes
            adjacency.setdefault(u, []).append(v)
            adjacency.setdefault(v, []).append(u)

        stack: list[Node] = [next(iter(nodes))]

        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            for neighbor in adjacency[node]:
                if neighbor not in visited:
                    stack.append(neighbor)

        return len(nodes) != len(visited)

    def __str__(self) -> str:
        s = ""
        for train in self.graph.trains:
            s += f"Train: {self.graph.trains[train]}\n"
            s += f"Visited Nodes: {[str(n) for n in self.nodes[train]]}\n"
            s += f"Used Edges: {[str(e) for e in self.edges[train]]}\n"
            s += f"Visited Cities: {[str(c) for c in self.cities[train]]}\n"

        s += f"Total Value: {self.value}\n"
        return s
