"""Reproducible synthetic comparison: naive ID-order vs OR-Tools, same staff."""
import json
from pathlib import Path
from .multi_optimizer import sample, optimize, travel_minutes


def baseline(visits, clinicians):
    """Naive round-robin ID-order assignment; may violate windows."""
    routes = [{"clinician_id": c.id, "visits": [], "travel_minutes": 0} for c in clinicians]
    states = [(c.x, c.y, c.shift_start) for c in clinicians]
    violations = 0
    for i, v in enumerate(sorted(visits, key=lambda v: v.id)):
        j = i % len(clinicians)
        x, y, clock = states[j]
        travel = travel_minutes((x, y), (v.x, v.y))
        arrival = max(clock + travel, v.earliest)
        end = arrival + v.duration
        if end > v.latest or end > clinicians[j].shift_end:
            violations += 1
        routes[j]["visits"].append({"id": v.id, "arrival": arrival, "departure": end, "travel": travel})
        routes[j]["travel_minutes"] += travel
        states[j] = (v.x, v.y, end)
    return {"routes": routes, "travel_minutes": sum(r["travel_minutes"] for r in routes),
            "assigned_count": len(visits), "constraint_violations": violations}


def run():
    visits, clinicians = sample()
    naive = baseline(visits, clinicians)
    optimized = optimize(visits, clinicians, time_limit_seconds=3)
    return {"data_type": "synthetic", "scenario": "6 visits, 2 clinicians, synthetic Euclidean travel",
            "baseline": naive, "optimized": optimized,
            "comparison_valid": naive["constraint_violations"] == 0 and optimized["constraint_violations"] == 0,
            "note": "Do not interpret travel reduction if baseline violates constraints; compare feasible schedules only."}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
