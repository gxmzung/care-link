"""Deterministic multi-scenario synthetic benchmark; no clinical claims."""
import json
import random
from statistics import mean, median
from .benchmark import baseline
from .multi_optimizer import Clinician, Visit, optimize


def scenario(seed, count=8):
    rng = random.Random(seed)
    clinicians = [Clinician("C01", 0, 0, 540, 1020),
                  Clinician("C02", 8, 8, 540, 1020)]
    visits = []
    for i in range(count):
        x, y = rng.randint(0, 10), rng.randint(0, 10)
        earliest = rng.choice([540, 600, 660, 720, 780])
        latest = min(1020, earliest + rng.choice([120, 180, 240]))
        visits.append(Visit(f"V{i+1:02d}", x, y, earliest, latest, 30))
    return visits, clinicians


def evaluate(seeds=range(10), count=8, time_limit_seconds=1):
    rows = []
    for seed in seeds:
        visits, clinicians = scenario(seed, count)
        control = baseline(visits, clinicians)
        result = optimize(visits, clinicians, time_limit_seconds)
        both_feasible = (control["constraint_violations"] == 0
                         and result["constraint_violations"] == 0
                         and control["assigned_count"] == result["assigned_count"] == count)
        reduction = (100 * (control["travel_minutes"] - result["travel_minutes"])
                     / control["travel_minutes"] if both_feasible and control["travel_minutes"] > 0 else None)
        rows.append({"seed": seed, "visits": count, "baseline_travel_minutes": control["travel_minutes"],
                     "optimized_travel_minutes": result["travel_minutes"],
                     "baseline_violations": control["constraint_violations"],
                     "optimized_violations": result["constraint_violations"],
                     "optimized_assigned": result["assigned_count"],
                     "both_feasible": both_feasible,
                     "travel_reduction_percent": round(reduction, 2) if reduction is not None else None})
    valid = [r["travel_reduction_percent"] for r in rows if r["travel_reduction_percent"] is not None]
    return {"data_type": "synthetic", "method": "seeded scenarios; ID-order baseline vs OR-Tools",
            "scenario_count": len(rows), "comparable_scenarios": len(valid),
            "comparison_rate_percent": round(100 * len(valid) / len(rows), 2) if rows else 0,
            "mean_reduction_percent_comparable_only": round(mean(valid), 2) if valid else None,
            "median_reduction_percent_comparable_only": round(median(valid), 2) if valid else None,
            "min_reduction_percent_comparable_only": min(valid) if valid else None,
            "max_reduction_percent_comparable_only": max(valid) if valid else None,
            "scenarios": rows,
            "limitations": "Only fully assigned, constraint-compliant schedules are compared. No real roads, patient data, or clinical validation."}


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))
