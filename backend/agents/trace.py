from datetime import datetime, timezone
import time
from functools import wraps
from typing import Callable

def make_trace_step(
    step_num: int,
    node_name: str,
    input_summary: str,
    output_summary: str,
    duration_ms: float
) -> dict:
    return {
        "step": step_num,
        "node": node_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_summary": input_summary,
        "output_summary": output_summary,
        "duration_ms": duration_ms
    }

def time_node(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(state: dict, *args, **kwargs):
        t0 = time.time()
        try:
            result = func(state, *args, **kwargs)
            duration_ms = (time.time() - t0) * 1000
            
            trace_list = state.get("trace", [])
            step_num = len(trace_list) + 1
            node_name = func.__name__
            
            trace_step = make_trace_step(
                step_num=step_num,
                node_name=node_name,
                input_summary=f"Entered {node_name}",
                output_summary=f"Completed {node_name} successfully",
                duration_ms=duration_ms
            )
            
            if result is None:
                result = {}
            if "trace" in result:
                result["trace"] = trace_list + [trace_step]
            else:
                result["trace"] = trace_list + [trace_step]
                
            return result
        except Exception as e:
            duration_ms = (time.time() - t0) * 1000
            trace_list = state.get("trace", [])
            step_num = len(trace_list) + 1
            node_name = func.__name__
            
            trace_step = make_trace_step(
                step_num=step_num,
                node_name=node_name,
                input_summary=f"Entered {node_name}",
                output_summary=f"Failed {node_name}: {str(e)}",
                duration_ms=duration_ms
            )
            raise
            
    return wrapper
