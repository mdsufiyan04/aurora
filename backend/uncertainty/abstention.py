from typing import List, Dict, Any

def check_abstention_rules(uncertainty_results: List[Dict[str, Any]], data_freshness_hours: float, sic_result: Dict[str, Any] = None, iceberg_result: Dict[str, Any] = None) -> Dict[str, Any]:
    rules = []
    abstained = False
    reasons = []
    
    # 1. Freshness
    passed = data_freshness_hours <= 24
    if not passed:
        abstained = True
        reasons.append(f"Data is {data_freshness_hours}h old (threshold: 24h)")
    rules.append({"rule": "data_freshness", "passed": passed, "detail": f"{data_freshness_hours}h"})
    
    # 2. Iceberg
    passed = True
    rules.append({"rule": "iceberg_uncertainty", "passed": passed, "detail": "N/A"})
    
    # 3. Feasibility
    max_feas = max([r.get('robust_feasibility', 1.0) for r in uncertainty_results]) if uncertainty_results else 1.0
    passed = max_feas >= 0.3
    if not passed:
        abstained = True
        reasons.append("No route remains feasible in >30% of scenarios")
    rules.append({"rule": "route_feasibility", "passed": passed, "detail": f"Max feasibility: {max_feas:.2f}"})
    
    # 4. High risk
    min_risk = min([r.get('expected_risk', 0.0) for r in uncertainty_results]) if uncertainty_results else 0.0
    passed = min_risk <= 0.4
    if not passed:
        abstained = True
        reasons.append("All routes have expected risk > 0.4")
    rules.append({"rule": "high_risk", "passed": passed, "detail": f"Min risk: {min_risk:.2f}"})
    
    # 5. SIC Forecast Uncertainty
    passed = True
    if sic_result and 'sigma' in sic_result and sic_result['sigma'] is not None:
        import numpy as np
        mean_sigma = np.nanmean(sic_result['sigma'])
        if mean_sigma > 15.0: # 15% out of 100
            passed = False
            abstained = True
            reasons.append("SIC forecast spread is too wide")
        rules.append({"rule": "sic_uncertainty", "passed": passed, "detail": f"Mean sigma: {mean_sigma:.2f}"})
    
    return {
        "abstained": abstained,
        "reason": " | ".join(reasons) if abstained else None,
        "checked_rules": rules
    }
