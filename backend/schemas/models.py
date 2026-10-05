from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=500)
    origin_lat: Optional[float] = None
    origin_lon: Optional[float] = None
    dest_lat: Optional[float] = None
    dest_lon: Optional[float] = None
    vessel_id: str = "SDA"
    horizon_hours: int = 120

class IntentResult(BaseModel):
    intent: str
    confidence: float
    slots: Dict[str, Any]

class RouteOption(BaseModel):
    label: str
    geometry: List[List[float]]
    distance_km: float
    travel_time_hours: float
    fuel_tonnes: float
    expected_risk: float
    max_sic: float
    p90_risk: Optional[float] = None
    p95_risk: Optional[float] = None
    robust_feasibility: Optional[float] = None
    feasibility_detail: Optional[str] = None

class TraceStep(BaseModel):
    step: int
    node: str
    timestamp: str
    input_summary: str
    output_summary: str
    duration_ms: float

class AnalysisResponse(BaseModel):
    run_id: str
    query: str
    intent: IntentResult
    routes: List[RouteOption]
    selected_route: Optional[RouteOption]
    abstained: bool = False
    abstention_reason: Optional[str] = None
    evidence: Dict[str, Any]
    trace: List[TraceStep]
    total_duration_seconds: float
    sensitivity: Optional[Dict[str, Any]] = None
    icebergs: List[Dict[str, Any]] = Field(default_factory=list)

class HealthResponse(BaseModel):
    status: str
    version: str
    data_freshness: Dict[str, Any]
