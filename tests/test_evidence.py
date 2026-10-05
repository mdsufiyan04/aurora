import pytest
from backend.evidence.composer import compose_evidence, generate_counterfactuals, format_evidence_for_frontend

def test_compose_evidence():
    selected = {"label": "SAFEST", "expected_risk": 0.05, "robust_feasibility": 1.0}
    all_routes = [
        selected,
        {"label": "FASTEST", "expected_risk": 0.15, "distance_km": 4000, "fuel_tonnes": 100, "travel_time_hours": 100},
        {"label": "BALANCED", "expected_risk": 0.10, "distance_km": 4200, "fuel_tonnes": 110, "travel_time_hours": 110}
    ]
    
    res = compose_evidence(
        selected_route=selected,
        all_routes=all_routes,
        uncertainty_results=all_routes,
        sensitivity_results={"stability_score": {"SAFEST": 1.0}},
        sic_result={"mean": [0.5], "sigma": [0.1]},
        iceberg_result={},
        data_freshness={},
        query="Safe route",
        intent="ROUTE_SAFETY"
    )
    
    assert "recommendation" in res
    assert "why_selected" in res
    assert "why_rejected" in res
    assert "provenance" in res
    assert "counterfactuals" in res
    
    # 2. test_why_selected_not_empty
    assert len(res["why_selected"]) >= 2
    
    # 3. test_why_rejected_covers_all_routes
    assert len(res["why_rejected"]) == 2
    
    # 4. test_provenance_has_datasets
    prov = res["provenance"]
    assert len(prov["datasets"]) == 4
    
    # 5. test_counterfactuals_have_penalty
    cf = res["counterfactuals"]
    assert len(cf) == 2
    assert "penalty_vs_selected" in cf[0]
    
    # 6. test_frontend_format
    fmt = res["frontend_format"]
    assert "headline" in fmt
    assert "summary_line" in fmt
    assert "cards" in fmt
    assert len(fmt["cards"]) == 3
