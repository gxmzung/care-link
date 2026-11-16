"""Constraint-aware deterministic greedy baseline, independent of OR-Tools."""
from .multi_optimizer import travel_minutes


def feasible_greedy(visits, clinicians):
    if not clinicians:
        raise ValueError("at least one clinician required")
    states = {c.id: (c.x, c.y, c.shift_start) for c in clinicians}
    routes = {c.id: {"clinician_id": c.id, "visits": [], "travel_minutes": 0} for c in clinicians}
    unassigned = []
    # Earliest deadline first; choose feasible clinician with earliest completion.
    for v in sorted(visits, key=lambda v: (v.latest, v.earliest, v.id)):
        choices = []
        for c in clinicians:
            x, y, now = states[c.id]
            travel = travel_minutes((x, y), (v.x, v.y))
            arrival = max(now + travel, v.earliest)
            finish = arrival + v.duration
            if finish <= min(v.latest, c.shift_end):
                choices.append((finish, travel, c.id, arrival))
        if not choices:
            unassigned.append(v.id)
            continue
        finish, travel, cid, arrival = min(choices)
        routes[cid]["visits"].append({"id": v.id, "arrival": arrival,
                                      "departure": finish, "travel": travel})
        routes[cid]["travel_minutes"] += travel
        states[cid] = (v.x, v.y, finish)
    return {"routes": [routes[c.id] for c in clinicians],
            "unassigned": unassigned,
            "assigned_count": len(visits) - len(unassigned),
            "travel_minutes": sum(r["travel_minutes"] for r in routes.values()),
            "constraint_violations": 0}
