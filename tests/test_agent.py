import pytest
from backend.agents.classifier import classify_intent, extract_slots
from backend.agents.graph import run_agent

def test_classify_intent():
    q1 = classify_intent("Is it safe to sail?")
    assert q1["intent"] == "ROUTE_SAFETY"
    
    q2 = classify_intent("Optimize my route.")
    assert q2["intent"] == "ROUTE_OPTIMIZE"
    
    q3 = classify_intent("Compare the trade-offs.")
    assert q3["intent"] == "ROUTE_COMPARE"
    
    q4 = classify_intent("Show me the sea-ice forecast.")
    assert q4["intent"] == "SIC_FORECAST"
    
    q5 = classify_intent("Track this iceberg.")
    assert q5["intent"] == "ICEBERG_TRACK"
    
    q6 = classify_intent("Why did you pick this route?")
    assert q6["intent"] == "EXPLAIN_ROUTE"

def test_extract_slots():
    slots = extract_slots("Navigate from Bharati to Maitri")
    assert slots["origin_lat"] == -69.4
    assert slots["origin_lon"] == 76.2
    assert slots["dest_lat"] == -70.7
    assert slots["dest_lon"] == 11.7

@pytest.mark.asyncio
async def test_full_agent_route_safety():
    query = "Is it safe to sail from Bharati to Maitri?"
    res = await run_agent(query)
    
    assert res["intent"] == "ROUTE_SAFETY"
    assert res["validation_passed"] is True
    assert "routes" in res
    assert len(res["routes"]) > 0
    assert res["selected_route"] is not None
    assert res["selected_route"]["label"] == "SAFEST"
    assert res["abstained"] is False
    assert len(res["trace"]) >= 10

@pytest.mark.asyncio
async def test_abstention_logic():
    # Will abstain if the risk is extremely high, but for now we just verify it doesn't crash
    res = await run_agent("Go to Maitri")
    assert res["validation_passed"] is True
    assert "routes" in res

@pytest.mark.asyncio
async def test_trace_has_all_nodes():
    query = "Test query"
    res = await run_agent(query)
    assert len(res["trace"]) >= 10
    nodes = [t["node"] for t in res["trace"]]
    assert "parse_query" in nodes
    assert "validate_inputs" in nodes
    assert "log_trace" in nodes
