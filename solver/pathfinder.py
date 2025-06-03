from collections import deque
from pprint import pprint

from pulp import const
from pulp import LpProblem, LpVariable, lpSum, PULP_CBC_CMD

from core.enums.direction import Direction
from core.game import Game
from core.hex import Hex
from core.railway import Railway
from core.settlement import City
from core.tile import Segment
from core.train import Train
from solver.graph import CityNode, Edge, Graph, JunctionNode, Node, Solution
from tools.exceptions import RuleError


class Pathfinder:
    game: Game

    def __init__(self, game: Game) -> None:
        self.game = game

    def solve_for(self, railway_id: str) -> Solution:
        railway = self.game.railways[railway_id]

        if not railway.floated:
            raise RuleError(
                f"Railway {railway_id} has not floated yet. (Railway is not active)"
            )
        if len(railway.trains) == 0:
            raise RuleError(f"Railway {railway_id} has no trains to find route for.")

        print(f"Finding best route for {railway_id} - Trains: {railway.trains}")

        graph = Graph(self.game, railway)

        problem = LpProblem("MaximalRouteFinding", const.LpMaximize)

        a = LpVariable.dicts(f"a", graph.trains, cat=const.LpBinary)  # train used
        v = [
            LpVariable.dicts(f"v_{train}", graph.nodes, cat=const.LpBinary)
            for train in graph.trains
        ]  # vertex visited
        e = [
            LpVariable.dicts(f"e_{train}", graph.edges, cat=const.LpBinary)
            for train in graph.trains
        ]  # edge visited
        c = [
            LpVariable.dicts(f"c_{train}", graph.cities, cat=const.LpBinary)
            for train in graph.trains
        ]  # city counted

        # Objective: Maximize visited city value
        # ∑f(i,t,p) * c[t][i]; ∀t∈T ∀i∈C
        problem += lpSum(
            self.game.board.settlement_at(city).revenue(
                graph.trains[train], self.game.phase
            )
            * c[train][city]
            for train in graph.trains
            for city in graph.cities
        )

        # Constraint: cannot visit more cites than the trains range (if used)
        # ∑_{i ∈ C} c[t][i] <= r_t * a[t]; ∀t∈T where t is non-diesel
        for train in graph.trains:
            if not graph.trains[train].diesel:
                problem += (
                    lpSum(c[train][city] for city in graph.cities)
                    <= graph.trains[train].range * a[train],
                    f"Train{train}MaxCitiesVisited",
                )

        # Constraint: train must visit at least two cities (if used)
        # ∑_{i ∈ C} c[t][i] >= 2 * a[t]; ∀t∈T
        for train in graph.trains:
            problem += (
                lpSum(c[train][city] for city in graph.cities) >= 2 * a[train],
                f"Train{train}MinCitiesVisited",
            )

        # Constraint: Trains can only score cities they pass through
        # c[t][i] == v[t][i]; ∀t∈T ∀i∈C
        for train in graph.trains:
            for city in graph.cities:
                problem += (
                    c[train][city] == v[train][city],
                    f"City{city}CountedIfVisitedByTrain{train}",
                )

        # Constraint: Trains cannot pass through edge another train has already used
        # ∑_{t ∈ T) [t][(i,j)] <= 1; ∀(i,j)∈E
        for edge in graph.edges:
            problem += (
                lpSum(e[train][edge] for train in graph.trains) <= 1,
                f"Edge{edge}UsedOnce",
            )

        # Constraint: Edge can only be visited if both nodes are visited.
        # e[t][(i,j)] <= v[t][i], e[t][(i,j)] <= v[t][j]; ∀t∈T
        for train in graph.trains:
            for edge in graph.edges:
                node1, node2 = edge
                problem += e[train][edge] <= v[train][node1]
                problem += e[train][edge] <= v[train][node2]

        # Constraint: Visited nodes need to have at least 2 adjacent edges
        for train in graph.trains:
            for node in graph.nodes:
                incident_edges = [edge for edge in graph.edges if node in edge]
                problem += (
                    lpSum(e[train][edge] for edge in incident_edges)
                    <= 2 * v[train][node],
                    f"Node{node}HasTwoOrOneEdgeUsedByTrain{train}",
                )

        # Constraint: Each route has to visit at least one home node (if train used)
        for train in graph.trains:
            problem += (
                lpSum(c[train][home] for home in graph.home_nodes) >= a[train],
                f"Train{train}UsesHomeStation",
            )

        # Constaint: Can't visit nodes if train not active
        for train in graph.trains:
            for node in graph.nodes:
                problem += (
                    v[train][node] <= a[train],
                    f"Node{node}CanOnlyBeVisitedIfTrain{train}Active",
                )

        # Constraint: Each junction needs to have equal about of used edges from both hexes for each route
        for train in graph.trains:
            for node in graph.nodes:
                if isinstance(node, JunctionNode):
                    incident_edges = [edge for edge in graph.edges if node in edge]
                    incident_from_sideA = [
                        edge for edge in incident_edges if edge.hex == node.hexes[0]
                    ]
                    incident_from_sideB = [
                        edge for edge in incident_edges if edge.hex == node.hexes[1]
                    ]
                    problem += (
                        lpSum(e[train][edge] for edge in incident_from_sideA)
                        == lpSum(e[train][edge] for edge in incident_from_sideB),
                        f"Juction{node}MustHaveEqualEdgesFromBothHexSidesForTrain{train}",
                    )

        # Constraint: City can have only one edge used if it's blocking
        for train in graph.trains:
            for node in graph.cities:
                settlement = self.game.board.settlement_at(node)
                if isinstance(settlement, City) and settlement.is_blocking_for(railway):
                    incident_edges = [edge for edge in graph.edges if node in edge]
                    problem += (
                        lpSum(e[train][edge] for edge in incident_edges)
                        == v[train][node],
                        f"City{node}MustBeTerminalForTrain{train}IfBlocking",
                    )

        # Constraint: Fence-post relationship between nodes and edges, enforcing a path (if active)
        for train in graph.trains:
            problem += lpSum(e[train][edge] for edge in graph.edges) == lpSum(v[train][node] for node in graph.nodes) - 1 * a[train]

        # solver = PULP_CBC_CMD(
        #     msg=True,
        #     options=[
        #         "primalTolerance=1e-11",
        #         "integerTolerance=1e-11",
        #         "ratioGap=0.0",  # optional: ensure optimality
        #     ],
        # )

        problem.solve()

        solution = Solution(graph, a, v, e, c)
        print(solution)

        return solution

if __name__ == "__main__":
    game = Game("1889")
    game.load("save.json")

    pathfinder = Pathfinder(game)
    pathfinder.solve_for("UR")

    print()
