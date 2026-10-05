from loguru import logger
import numpy as np
from backend.agents.state import AgentState
from backend.agents.classifier import classify_intent, extract_slots
from backend.agents.trace import time_node
from backend.science.icenet_adapter import forecast_sic
from backend.science.iceberg_model import predict_iceberg_trajectory
from backend.science.route_optimizer import build_hazard_field, optimize_multiple_routes, pareto_filter as do_pareto_filter
from backend.uncertainty import propagate_route_uncertainty, compute_weight_sensitivity, check_abstention_rules
from backend.evidence.composer import compose_evidence as create_evidence

@time_node
def parse_query(state: AgentState) -> dict:
    query = state.get("query", "")
    intent_res = classify_intent(query)
    slots = extract_slots(query)
    
    return {
        "intent": intent_res["intent"],
        "intent_confidence": intent_res["confidence"],
        "slots": slots
    }

@time_node
def validate_inputs(state: AgentState) -> dict:
    slots = state.get("slots", {})
    if "origin_lat" not in slots or "dest_lat" not in slots:
        return {
            "validation_passed": False,
            "validation_error": "Missing origin or destination coordinates"
        }
    return {"validation_passed": True, "validation_error": None}

@time_node
def fetch_sic(state: AgentState) -> dict:
    res = forecast_sic(threshold=0.7)
    return {"sic_result": res}

@time_node
def fetch_icebergs(state: AgentState) -> dict:
    slots = state.get("slots", {})
    res = predict_iceberg_trajectory(
        start_lat=slots.get("origin_lat", -69.4),
        start_lon=slots.get("origin_lon", 76.2),
        horizon_hours=120
    )
    return {"iceberg_result": res}

@time_node
def build_hazard(state: AgentState) -> dict:
    sic_res = state.get("sic_result", {})
    ice_res = state.get("iceberg_result", {})
    hf = build_hazard_field(sic_res, ice_res)
    return {"hazard_field": hf}

@time_node
def optimize_routes(state: AgentState) -> dict:
    slots = state.get("slots", {})
    from backend.science.route_optimizer import load_grid_data
    grid = load_grid_data()
    routes = optimize_multiple_routes(
        start_lat=slots["origin_lat"],
        start_lon=slots["origin_lon"],
        end_lat=slots["dest_lat"],
        end_lon=slots["dest_lon"],
        hazard=state.get("hazard_field"),
        grid=grid
    )
    return {"routes": routes}

@time_node
def propagate_uncertainty(state: AgentState) -> dict:
    logger.info("Propagating uncertainty via Monte Carlo")
    routes = state.get("routes", [])
    if not routes:
        return {"routes_with_uncertainty": [], "sensitivity_results": {}}
        
    updated_routes = propagate_route_uncertainty(
        routes=routes,
        hazard_field=state.get("hazard_field"),
        sic_result=state.get("sic_result"),
        iceberg_result=state.get("iceberg_result"),
        scenarios=50
    )
    
    sensitivity = compute_weight_sensitivity(updated_routes)
    
    return {
        "routes_with_uncertainty": updated_routes,
        "sensitivity_results": sensitivity,
        "routes": updated_routes  # Update main routes list with new fields for pareto_filter
    }

@time_node
def pareto_filter(state: AgentState) -> dict:
    routes = state.get("routes", [])
    p_routes = do_pareto_filter(routes)
    return {"pareto_routes": p_routes}

@time_node
def select_route(state: AgentState) -> dict:
    intent = state.get("intent", "ROUTE_OPTIMIZE")
    routes = state.get("pareto_routes", [])
    
    if not routes:
        return {"selected_route": None}
        
    selected = routes[0]
    for r in routes:
        if intent == "ROUTE_SAFETY" and r["label"] == "SAFEST":
            selected = r
        elif intent == "ROUTE_OPTIMIZE" and r["label"] == "FASTEST":
            selected = r
        elif intent == "ROUTE_COMPARE" and r["label"] == "BALANCED":
            selected = r
            
    return {"selected_route": selected}

@time_node
def compose_evidence(state: AgentState) -> dict:
    selected = state.get("selected_route")
    routes = state.get("routes_with_uncertainty", [])
    if not routes and state.get("routes"):
        routes = state.get("routes", [])
        
    packet = create_evidence(
        selected_route=selected,
        all_routes=routes,
        uncertainty_results=routes,
        sensitivity_results=state.get("sensitivity_results", {}),
        sic_result=state.get("sic_result", {}),
        iceberg_result=state.get("iceberg_result", {}),
        data_freshness={},
        query=state.get("query", ""),
        intent=state.get("intent", "ROUTE_OPTIMIZE")
    )
    return {"evidence": packet}

@time_node
def check_abstention(state: AgentState) -> dict:
    updated_routes = state.get("routes_with_uncertainty", [])
    sic_res = state.get("sic_result", {})
    ice_res = state.get("iceberg_result", {})
    
    # Assume data is fresh for MVP demo, pass 1.0 hour
    res = check_abstention_rules(
        uncertainty_results=updated_routes,
        data_freshness_hours=1.0,
        sic_result=sic_res,
        iceberg_result=ice_res
    )
    
    evidence = state.get("evidence", {})
    evidence["abstention_rules"] = res["checked_rules"]
    
    return {
        "abstained": res["abstained"],
        "abstention_reason": res["reason"],
        "evidence": evidence
    }

@time_node
def log_trace(state: AgentState) -> dict:
    # Just a pass-through, trace is appended by decorator
    return {}
