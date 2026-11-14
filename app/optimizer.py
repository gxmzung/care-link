"""Synthetic visit scheduling with time-window constraints. No patient data."""
from dataclasses import dataclass
from math import hypot

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


def schedule(visits, start=(0, 0), start_minute=540, end_minute=1080):
    """Deterministic nearest-feasible greedy baseline; not globally optimal."""
    remaining = list(visits)
    current = start
    now = start_minute
    route = []
    total_travel = 0
    while remaining:
        feasible = []
        for v in remaining:
            t = travel_minutes(current, (v.x, v.y))
            arrival = max(now + t, v.earliest)
            if arrival + v.duration <= min(v.latest, end_minute):
                feasible.append((t, arrival, v.id, v))
        if not feasible:
            break
        t, arrival, _, v = min(feasible)
        route.append({"id": v.id, "arrival": arrival, "departure": arrival + v.duration, "travel": t})
        total_travel += t
        now = arrival + v.duration
        current = (v.x, v.y)
        remaining.remove(v)
    return {"route": route, "unassigned": [v.id for v in remaining], "travel_minutes": total_travel, "assigned_count": len(route)}


def sample_visits():
    return [
        Visit('V01', 2, 3, 540, 780), Visit('V02', 6, 2, 600, 960),
        Visit('V03', 3, 7, 570, 900), Visit('V04', 8, 6, 660, 1020),
        Visit('V05', 1, 8, 540, 1080), Visit('V06', 7, 9, 720, 1080),
    ]
