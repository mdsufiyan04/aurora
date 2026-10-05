import numpy as np
from typing import List, Dict, Any

def compute_weight_sensitivity(routes: List[Dict[str, Any]], base_weights: Dict[str, float] = None, n_configs: int = 20) -> Dict[str, Any]:
    if not routes:
        return {}
        
    if base_weights is None:
        base_weights = {"w_time": 0.25, "w_fuel": 0.2, "w_sic": 0.25, "w_iceberg": 0.25, "w_weather": 0.05}
        
    winner_counts = {r['label']: 0 for r in routes}
    
    times = np.array([r.get('travel_time_hours', 1.0) for r in routes])
    fuels = np.array([r.get('fuel_tonnes', 1.0) for r in routes])
    risks = np.array([r.get('expected_risk', 1.0) for r in routes])
    
    def norm(arr):
        mn, mx = np.min(arr), np.max(arr)
        if mx == mn: return np.zeros_like(arr)
        return (arr - mn) / (mx - mn)
        
    t_norm = norm(times)
    f_norm = norm(fuels)
    r_norm = norm(risks)
    
    for _ in range(n_configs):
        w_t = base_weights['w_time'] * np.random.uniform(0.7, 1.3)
        w_f = base_weights['w_fuel'] * np.random.uniform(0.7, 1.3)
        w_s = base_weights['w_sic'] * np.random.uniform(0.7, 1.3)
        w_i = base_weights['w_iceberg'] * np.random.uniform(0.7, 1.3)
        w_w = base_weights['w_weather'] * np.random.uniform(0.7, 1.3)
        
        tot = w_t + w_f + w_s + w_i + w_w
        w_t, w_f, w_s, w_i, w_w = w_t/tot, w_f/tot, w_s/tot, w_i/tot, w_w/tot
        
        costs = w_t * t_norm + w_f * f_norm + w_s * r_norm + w_i * r_norm + w_w * r_norm
        winner_idx = int(np.argmin(costs))
        winner_counts[routes[winner_idx]['label']] += 1
        
    stability = {k: float(v/n_configs) for k, v in winner_counts.items()}
    best_label = max(stability.items(), key=lambda x: x[1])[0]
    best_score = stability[best_label]
    
    return {
        "total_configs": n_configs,
        "winner_counts": winner_counts,
        "stability_score": stability,
        "stable_recommendation": best_label,
        "interpretation": f"{best_label} route is stable under {int(best_score*100)}% of weight configurations"
    }
