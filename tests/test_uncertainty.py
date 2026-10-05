import pytest
from backend.uncertainty import propagate_route_uncertainty, compute_iceberg_proximity, compute_weight_sensitivity, check_abstention_rules

def test_propagate_route_uncertainty():
    routes = [{"geometry": [[-69.4, 76.2], [-70.7, 11.7]], "max_sic": 50.0, "expected_risk": 0.2}]
    hazard_field = None
    sic_result = {"mean": None, "sigma": None}
    iceberg_result = {"ensemble_trajectories": [{"lats": [-70.0], "lons": [50.0]}]}
    
    res = propagate_route_uncertainty(routes, hazard_field, sic_result, iceberg_result, scenarios=50)
    
    assert len(res) == 1
    assert 0.0 <= res[0]["robust_feasibility"] <= 1.0
    assert res[0]["scenarios_evaluated"] == 50

def test_iceberg_proximity():
    route_geometry = [[0.0, 0.0], [1.0, 1.0]]
    iceberg_scenarios = [{"lat": 0.5, "lon": 0.5}]
    
    res = compute_iceberg_proximity(route_geometry, iceberg_scenarios, threshold_km=20)
    assert "min_km" in res
    assert "p90_km" in res
    assert res["min_km"] >= 0

def test_weight_sensitivity():
    routes = [
        {"label": "FASTEST", "travel_time_hours": 10, "fuel_tonnes": 5, "expected_risk": 0.5},
        {"label": "SAFEST", "travel_time_hours": 20, "fuel_tonnes": 10, "expected_risk": 0.1},
        {"label": "BALANCED", "travel_time_hours": 15, "fuel_tonnes": 7.5, "expected_risk": 0.3}
    ]
    
    res = compute_weight_sensitivity(routes, n_configs=20)
    
    assert "stability_score" in res
    scores = res["stability_score"]
    assert abs(sum(scores.values()) - 1.0) < 1e-6
    assert res["stable_recommendation"] in ["FASTEST", "SAFEST", "BALANCED"]

def test_abstention_fresh_data():
    res = check_abstention_rules([], data_freshness_hours=1.0)
    assert not res["abstained"]

def test_abstention_stale_data():
    res = check_abstention_rules([], data_freshness_hours=30.0)
    assert res["abstained"]

