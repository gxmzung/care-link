from app.feasible_baseline import feasible_greedy
from app.multi_optimizer import Clinician, Visit

def test_feasible_baseline_all_assignable():
    result = feasible_greedy([Visit("A", 1, 1, 540, 900), Visit("B", 2, 2, 540, 900)], [Clinician("C")])
    assert result["assigned_count"] == 2
    assert result["constraint_violations"] == 0
    assert result["unassigned"] == []

def test_feasible_baseline_drops_impossible():
    result = feasible_greedy([Visit("A", 1000, 1000, 540, 550)], [Clinician("C")])
    assert result["assigned_count"] == 0
    assert result["unassigned"] == ["A"]
