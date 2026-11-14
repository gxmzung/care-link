from app.benchmark import run, baseline
from app.multi_optimizer import sample


def test_benchmark_reproducible_structure():
    result = run()
    assert result["data_type"] == "synthetic"
    assert result["baseline"]["assigned_count"] == 6
    assert result["optimized"]["assigned_count"] + len(result["optimized"]["unassigned"]) == 6
    assert result["optimized"]["constraint_violations"] == 0


def test_baseline_has_same_clinicians():
    visits, clinicians = sample()
    result = baseline(visits, clinicians)
    assert len(result["routes"]) == len(clinicians)
