"""Multi-clinician synthetic visit routing with OR-Tools VRPTW.

All coordinates and travel times are synthetic. No clinical decisions.
"""
from dataclasses import dataclass
from math import hypot

from ortools.constraint_solver import pywrapcp, routing_enums_pb2


@dataclass(frozen=True)
class Clinician:
    id: str
    x: float = 0
    y: float = 0
    shift_start: int = 540
    shift_end: int = 1080


@dataclass(frozen=True)
class Visit:
    id: str
    x: float
    y: float
    earliest: int
    latest: int
    duration: int = 30


def travel_minutes(a, b):
    return round(hypot(a[0] - b[0], a[1] - b[1]) * 5)


def optimize(visits, clinicians, time_limit_seconds=3):
    """Minimize synthetic travel and dropped visits under time windows.

    Returns deterministic, explicitly validated schedules. Dropping a visit
    costs 100000 units; a feasible schedule is preferred over a dropped visit.
    """
    if not clinicians:
        raise ValueError("at least one clinician required")
    if len({v.id for v in visits}) != len(visits):
        raise ValueError("duplicate visit id")
    if len({c.id for c in clinicians}) != len(clinicians):
        raise ValueError("duplicate clinician id")
    if any(v.earliest >= v.latest or v.duration <= 0 for v in visits):
        raise ValueError("invalid visit window")
    if any(c.shift_start >= c.shift_end for c in clinicians):
        raise ValueError("invalid clinician shift")
    if not visits:
        return {"routes": [{"clinician_id": c.id, "visits": [], "travel_minutes": 0} for c in clinicians],
                "unassigned": [], "assigned_count": 0, "travel_minutes": 0, "constraint_violations": 0}

    impossible = [v.id for v in visits if v.latest - v.duration < v.earliest]
    if impossible:
        feasible = [v for v in visits if v.id not in set(impossible)]
        result = optimize(feasible, clinicians, time_limit_seconds)
        result["unassigned"] = [v.id for v in visits if v.id in set(result["unassigned"]) or v.id in set(impossible)]
        return result

    # One distinct start and end depot per clinician, so clinician origins may differ.
    n = len(visits)
    k = len(clinicians)
    coords = [(v.x, v.y) for v in visits] + [(c.x, c.y) for c in clinicians] * 2
    starts = list(range(n, n + k))
    ends = list(range(n + k, n + 2 * k))
    manager = pywrapcp.RoutingIndexManager(len(coords), k, starts, ends)
    routing = pywrapcp.RoutingModel(manager)
    matrix = [[travel_minutes(a, b) for b in coords] for a in coords]

    def distance(from_index, to_index):
        a, b = manager.IndexToNode(from_index), manager.IndexToNode(to_index)
        if b >= n + k:  # no return-to-depot requirement in this MVP
            return 0
        return matrix[a][b]

    distance_id = routing.RegisterTransitCallback(distance)
    routing.SetArcCostEvaluatorOfAllVehicles(distance_id)

    def time_transit(from_index, to_index):
        node = manager.IndexToNode(from_index)
        service = visits[node].duration if node < n else 0
        return service + distance(from_index, to_index)

    time_id = routing.RegisterTransitCallback(time_transit)
    routing.AddDimension(time_id, 1440, 2880, False, "Time")
    time_dim = routing.GetDimensionOrDie("Time")
    for i, v in enumerate(visits):
        idx = manager.NodeToIndex(i)
        # latest is latest permissible completion time
        time_dim.CumulVar(idx).SetRange(v.earliest, v.latest - v.duration)
        routing.AddDisjunction([idx], 100000)
    for vehicle, c in enumerate(clinicians):
        time_dim.CumulVar(routing.Start(vehicle)).SetRange(c.shift_start, c.shift_start)
        time_dim.CumulVar(routing.End(vehicle)).SetRange(c.shift_start, c.shift_end)
        routing.AddVariableMinimizedByFinalizer(time_dim.CumulVar(routing.End(vehicle)))

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = max(1, int(time_limit_seconds))
    solution = routing.SolveWithParameters(params)
    if solution is None:
        raise RuntimeError("no feasible routing solution")

    routes = []
    assigned = set()
    total_travel = 0
    violations = 0
    for vehicle, c in enumerate(clinicians):
        idx = routing.Start(vehicle)
        rows = []
        previous_node = manager.IndexToNode(idx)
        last_end = c.shift_start
        vehicle_travel = 0
        while not routing.IsEnd(idx):
            next_idx = solution.Value(routing.NextVar(idx))
            if routing.IsEnd(next_idx):
                break
            node = manager.IndexToNode(next_idx)
            v = visits[node]
            arrival = solution.Value(time_dim.CumulVar(next_idx))
            move = matrix[previous_node][node]
            rows.append({"id": v.id, "arrival": arrival, "departure": arrival + v.duration, "travel": move})
            if arrival < max(last_end + move, v.earliest) or arrival + v.duration > min(v.latest, c.shift_end):
                violations += 1
            last_end = arrival + v.duration
            previous_node = node
            vehicle_travel += move
            assigned.add(v.id)
            idx = next_idx
        total_travel += vehicle_travel
        routes.append({"clinician_id": c.id, "visits": rows, "travel_minutes": vehicle_travel})
    return {"routes": routes, "unassigned": [v.id for v in visits if v.id not in assigned],
            "assigned_count": len(assigned), "travel_minutes": total_travel,
            "constraint_violations": violations}


def sample():
    return ([Visit("V01", 2, 3, 540, 780), Visit("V02", 6, 2, 600, 960),
             Visit("V03", 3, 7, 570, 900), Visit("V04", 8, 6, 660, 1020),
             Visit("V05", 1, 8, 540, 1080), Visit("V06", 7, 9, 720, 1080)],
            [Clinician("C01"), Clinician("C02", 8, 8)])
