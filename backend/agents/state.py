from typing import TypedDict, Optional, List, Dict, Any
import numpy as np

class AgentState(TypedDict, total=False):
    run_id: str
    query: str
    intent: Optional[str]
    intent_confidence: Optional[float]
    slots: Dict[str, Any]
    validation_passed: bool
    validation_error: Optional[str]
    sic_result: Optional[Dict[str, Any]]
    iceberg_result: Optional[Dict[str, Any]]
    hazard_field: Optional[np.ndarray]
    routes: Optional[List[Dict[str, Any]]]
    routes_with_uncertainty: Optional[List[Dict[str, Any]]]
    sensitivity_results: Optional[Dict[str, Any]]
    pareto_routes: Optional[List[Dict[str, Any]]]
    selected_route: Optional[Dict[str, Any]]
    abstained: bool
    abstention_reason: Optional[str]
    evidence: Optional[Dict[str, Any]]
    trace: List[Dict[str, Any]]
    start_time: float
