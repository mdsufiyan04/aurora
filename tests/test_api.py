import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data

def test_analyze_stub():
    payload = {
        "query": "Find a safe route to Maitri station",
        "origin_lat": -69.4,
        "origin_lon": 76.2,
        "dest_lat": -70.7,
        "dest_lon": 11.7
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["query"] == payload["query"]
    assert "run_id" in data
    assert len(data["routes"]) > 0
    assert data["intent"]["intent"] == "ROUTE_OPTIMIZE"

def test_trace_retrieval():
    payload = {
        "query": "Trace this query"
    }
    res_post = client.post("/analyze", json=payload)
    run_id = res_post.json()["run_id"]
    
    res_trace = client.get(f"/trace/{run_id}")
    assert res_trace.status_code == 200
    traces = res_trace.json()
    assert len(traces) > 0
    assert traces[0]["node"] == "router"
