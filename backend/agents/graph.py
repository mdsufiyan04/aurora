import uuid
import time
from langgraph.graph import StateGraph, START, END
from backend.agents.state import AgentState
from backend.agents.nodes import (
    parse_query, validate_inputs, fetch_sic, fetch_icebergs,
    build_hazard, optimize_routes, propagate_uncertainty, pareto_filter, select_route,
    compose_evidence, check_abstention, log_trace
)

workflow = StateGraph(AgentState)

workflow.add_node("parse_query", parse_query)
workflow.add_node("validate_inputs", validate_inputs)
workflow.add_node("fetch_sic", fetch_sic)
workflow.add_node("fetch_icebergs", fetch_icebergs)
workflow.add_node("build_hazard", build_hazard)
workflow.add_node("optimize_routes", optimize_routes)
workflow.add_node("propagate_uncertainty", propagate_uncertainty)
workflow.add_node("pareto_filter", pareto_filter)
workflow.add_node("select_route", select_route)
workflow.add_node("compose_evidence", compose_evidence)
workflow.add_node("check_abstention", check_abstention)
workflow.add_node("log_trace", log_trace)

workflow.add_edge(START, "parse_query")
workflow.add_edge("parse_query", "validate_inputs")

def validation_condition(state: AgentState) -> str:
    if state.get("validation_passed", False):
        return "fetch_sic"
    return "log_trace"

def route_by_intent(state):
    if not state.get("validation_passed", False):
        return "log_trace"
        
    intent = state.get("intent")
    if intent == "SIC_FORECAST":
        return "sic_only"
    elif intent == "ICEBERG_TRACK":
        return "iceberg_only"
    else:
        return "full_route"

workflow.add_conditional_edges("validate_inputs", route_by_intent, {
    "sic_only": "fetch_sic",
    "iceberg_only": "fetch_icebergs",
    "full_route": "fetch_sic",
    "log_trace": "log_trace"
})

workflow.add_conditional_edges(
    "fetch_sic",
    lambda s: "sic_done" if s.get("intent") == "SIC_FORECAST" else "continue",
    {
        "sic_done": "log_trace",
        "continue": "fetch_icebergs",
    }
)

workflow.add_edge("fetch_icebergs", "build_hazard")
workflow.add_edge("build_hazard", "optimize_routes")
workflow.add_edge("optimize_routes", "propagate_uncertainty")
workflow.add_edge("propagate_uncertainty", "pareto_filter")
workflow.add_edge("pareto_filter", "select_route")
workflow.add_edge("select_route", "compose_evidence")
workflow.add_edge("compose_evidence", "check_abstention")
workflow.add_edge("check_abstention", "log_trace")
workflow.add_edge("log_trace", END)

graph = workflow.compile()

async def run_agent(query: str, slots: dict = None) -> dict:
    initial_state = {
        "run_id": str(uuid.uuid4()),
        "query": query,
        "slots": slots or {},
        "trace": [],
        "start_time": time.time()
    }
    result = await graph.ainvoke(initial_state)
    return result
