from fastapi.testclient import TestClient
from app.main import app

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
