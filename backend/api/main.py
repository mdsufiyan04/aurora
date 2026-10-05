import uuid
import time
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from backend.schemas.models import (
    HealthResponse,
    QueryRequest,
    AnalysisResponse,
    IntentResult,
    RouteOption,
    TraceStep
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AURORA API starting up...")
    yield
    logger.info("AURORA API shutting down...")

app = FastAPI(title="AURORA API", lifespan=lifespan)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://aurora-beta-neon.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory trace store for MVP
TRACE_STORE: Dict[str, List[TraceStep]] = {}



@app.get("/health", response_model=HealthResponse)
async def health_check():
    logger.info("Health check requested")
    import os
    
    def get_file_age(path: str) -> dict:
        if not os.path.exists(path):
            return {"age_hours": 999.0, "valid_time": "Not found"}
        mtime = os.path.getmtime(path)
        age_hours = (time.time() - mtime) / 3600.0
        return {"age_hours": round(age_hours, 1), "valid_time": time.ctime(mtime)}
        
    return HealthResponse(
        status="ok",
        version="0.1.0",
        data_freshness={
            "sic": get_file_age("data/cached/sic_forecast.nc"),
            "forcing": get_file_age("data/cached/forcing.nc"),
            "icebergs": get_file_age("data/cached/forcing.nc")
        }
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: QueryRequest):
    from backend.agents.graph import run_agent
    logger.info(f"Received query: {request.query}")
    result = await run_agent(request.query)
    
    # Store trace for /trace/{run_id}
    TRACE_STORE[result["run_id"]] = result["trace"]
    
    routes = result.get("pareto_routes", []) or []
    selected = result.get("selected_route", None)
    
    # Extract iceberg data if present
    icebergs_list = []
    ice_res = result.get("evidence", {}).get("iceberg_result") or result.get("iceberg_result", {})
    if ice_res and "current_position" in ice_res:
        # Create a basic GeoJSON polygon for the envelope using ensemble endpoints (mock p95 for MVP)
        import scipy.spatial as spatial
        import numpy as np
        envelope = None
        if "ensemble" in ice_res:
            pts = []
            for member in ice_res["ensemble"]:
                if member["lat"] and member["lon"]:
                    pts.append([member["lon"][-1], member["lat"][-1]])
            if len(pts) > 2:
                try:
                    hull = spatial.ConvexHull(pts)
                    hull_pts = [pts[i] for i in hull.vertices]
                    hull_pts.append(hull_pts[0]) # close polygon
                    envelope = {
                        "type": "Polygon",
                        "coordinates": [hull_pts]
                    }
                except Exception:
                    pass
                    
        icebergs_list.append({
            "id": "BERG-1",
            "lat": ice_res["current_position"]["lat"],
            "lon": ice_res["current_position"]["lon"],
            "size_km": 2.5,
            "envelope": envelope
        })
    
    return AnalysisResponse(
        run_id=result["run_id"],
        query=result["query"],
        intent=IntentResult(
            intent=result.get("intent", "ROUTE_OPTIMIZE"),
            confidence=result.get("intent_confidence", 0.0),
            slots=result.get("slots", {})
        ),
        routes=[RouteOption(**{**r, "max_sic": r.get("max_sic_encountered", 0.0)}) for r in routes],
        selected_route=RouteOption(**{**selected, "max_sic": selected.get("max_sic_encountered", 0.0)}) if selected else None,
        abstained=result.get("abstained", False),
        abstention_reason=result.get("abstention_reason", None),
        evidence=result.get("evidence", {}),
        trace=[TraceStep(**t) for t in result["trace"]],
        total_duration_seconds=time.time() - result["start_time"],
        sensitivity=result.get("sensitivity_results", None),
        icebergs=icebergs_list
    )

@app.get("/trace/{run_id}", response_model=List[TraceStep])
async def get_trace(run_id: str):
    logger.info(f"Trace requested for run_id: {run_id}")
    if run_id not in TRACE_STORE:
        raise HTTPException(status_code=404, detail="Trace not found")
    return TRACE_STORE[run_id]

@app.get("/map/sic-field")
async def get_sic_field():
    """Return SIC field as base64 PNG + bounds for map overlay."""
    from backend.science.icenet_adapter import forecast_sic
    from PIL import Image
    import io
    import base64
    import numpy as np
    
    result = forecast_sic(threshold=0.7)
    mean = result['mean']  # 2D array
    
    # Normalize to 0-255
    min_val = np.nanmin(mean)
    max_val = np.nanmax(mean)
    if max_val > min_val:
        normalized = ((mean - min_val) / (max_val - min_val) * 255)
    else:
        normalized = mean * 0
    normalized = np.nan_to_num(normalized, nan=0.0).astype(np.uint8)
    
    # Create RGBA image with blue-white gradient
    img = Image.fromarray(normalized, mode='L').convert('RGBA')
    # Apply color map: low = blue, high = light blue/white
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()
    
    return {
        "image_base64": f"data:image/png;base64,{b64}",
        "bounds": {
            "west": -20, "east": 90,
            "south": -75, "north": -65
        }
    }
