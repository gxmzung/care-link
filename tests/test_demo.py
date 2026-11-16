from fastapi.testclient import TestClient
from app.main import app
import app.demo as demo

client = TestClient(app)

def test_demo_page():
    r = client.get("/demo")
    assert r.status_code == 200
    assert "CARE-LINK" in r.text
    assert "합성" in r.text

def test_demo_result():
    r = client.get("/demo/result")
    assert r.status_code == 200
    d = r.json()
    assert d["data_type"] == "synthetic"
    assert d["optimized"]["constraint_violations"] == 0


def test_demo_dashboard_structure():
    r = client.get("/demo")
    assert r.status_code == 200
    assert "방문의료 일정 최적화 대시보드" in r.text
    assert "id=\"scenario-chart\"" in r.text
    assert "id=\"single-comparison\"" in r.text
    assert "실제 의료기관 도입·의료적 판단·경제적 절감 효과는 검증되지 않았습니다" in r.text


def test_demo_scenarios_schema_and_refresh(monkeypatch):
    payload = {
        "data_type": "synthetic",
        "scenario_count": 1,
        "comparable_scenarios": 1,
        "mean_reduction_percent_comparable_only": 25.0,
        "median_reduction_percent_comparable_only": 25.0,
        "baseline_assigned": 8,
        "optimized_assigned": 8,
        "both_feasible": 1,
        "optimized_violations": 0,
        "scenarios": [{"seed": 0, "visits": 8, "travel_reduction_percent": 25.0}],
    }
    refresh_flags = []

    def fake_results(*, refresh=False):
        refresh_flags.append(refresh)
        return payload

    monkeypatch.setattr(demo, "_get_scenario_results", fake_results)
    response = client.get("/demo/scenarios")
    refreshed = client.post("/demo/scenarios/refresh")

    assert response.status_code == refreshed.status_code == 200
    assert refresh_flags == [False, True]
    required = {
        "scenario_count", "comparable_scenarios",
        "mean_reduction_percent_comparable_only",
        "median_reduction_percent_comparable_only", "scenarios",
        "baseline_assigned", "optimized_assigned", "both_feasible",
        "optimized_violations",
    }
    assert required <= response.json().keys()


def test_invalid_comparison_ui_has_no_hardcoded_improvement():
    page = client.get("/demo").text
    script = client.get("/static/dashboard.js").text

    assert "20.8%" not in page
    assert "43.51" not in page
    assert "data.comparison_valid === true" in script
    assert "시간 제약 불충족 · 이동시간 비교 불가" in script
