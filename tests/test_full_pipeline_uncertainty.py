import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

def test_full_pipeline_with_uncertainty():
    client = TestClient(app)
    response = client.post("/analyze", json={"query": "Is it safe to sail from Bharati to Maitri?"})
    assert response.status_code == 200
    
    data = response.json()
    assert "sensitivity" in data
    assert data["sensitivity"] is not None
    assert "stability_score" in data["sensitivity"]
    
    routes = data.get("routes", [])
    assert len(routes) > 0
    
    for route in routes:
        assert "robust_feasibility" in route
        assert route["robust_feasibility"] is not None
        assert "feasibility_detail" in route
        assert route["feasibility_detail"] is not None
