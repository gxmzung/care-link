from app.scenario_benchmark import evaluate, scenario

def test_scenarios_reproducible():
    a, _ = scenario(42)
    b, _ = scenario(42)
    assert a == b
    assert len(a) == 8

def test_evaluation_schema_and_validity():
    data = evaluate(seeds=[0, 1], count=6, time_limit_seconds=1)
    assert data["scenario_count"] == 2
    assert 0 <= data["comparable_scenarios"] <= 2
    for row in data["scenarios"]:
        assert row["optimized_violations"] == 0
        if not row["both_feasible"]:
            assert row["travel_reduction_percent"] is None
        else:
            assert row["optimized_assigned"] == 6
