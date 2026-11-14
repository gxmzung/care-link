from app.optimizer import Visit, schedule, sample_visits
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_sample_schedule_respects_windows():
    visits = {v.id: v for v in sample_visits()}
    plan = schedule(list(visits.values()))
    assert plan['assigned_count'] + len(plan['unassigned']) == len(visits)
    for row in plan['route']:
        v = visits[row['id']]
        assert row['arrival'] >= v.earliest
        assert row['departure'] <= v.latest

def test_infeasible_visit_is_unassigned():
    result = schedule([Visit('X', 10, 10, 540, 550)])
    assert result['unassigned'] == ['X']

def test_api_sample():
    response = client.get('/api/sample')
    assert response.status_code == 200
    assert response.json()['data_type'] == 'synthetic'

def test_duplicate_ids_rejected():
    v = {'id':'X','x':1,'y':1,'earliest':540,'latest':900}
    assert client.post('/api/plan', json={'visits':[v,v]}).status_code == 422

def test_invalid_window_rejected():
    v = {'id':'X','x':1,'y':1,'earliest':900,'latest':540}
    assert client.post('/api/plan', json={'visits':[v]}).status_code == 422
