from app.multi_optimizer import Clinician, Visit, optimize, sample


def test_sample_all_assigned_without_violations():
    visits, clinicians = sample()
    result = optimize(visits, clinicians, 1)
    assert result["assigned_count"] == len(visits)
    assert result["constraint_violations"] == 0
    assert len(result["routes"]) == 2


def test_infeasible_visit_dropped():
    result = optimize([Visit("X", 50, 50, 540, 550, 30)], [Clinician("C")], 1)
    assert result["unassigned"] == ["X"]
    assert result["assigned_count"] == 0


def test_empty_visits():
    result = optimize([], [Clinician("C")], 1)
    assert result["assigned_count"] == 0


def test_duplicate_ids_rejected():
    visit = Visit("X", 1, 1, 540, 900)
    try:
        optimize([visit, visit], [Clinician("C")], 1)
        assert False
    except ValueError:
        pass


def test_visits_respect_clinician_shift():
    result = optimize([Visit("X", 1, 1, 540, 900)], [Clinician("C", shift_start=600, shift_end=720)], 1)
    assert result["assigned_count"] == 1
    assert result["routes"][0]["visits"][0]["arrival"] >= 600
