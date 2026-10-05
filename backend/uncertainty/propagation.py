import numpy as np
from loguru import logger
from typing import List, Dict, Any

def compute_iceberg_proximity(route_geometry: List[List[float]], iceberg_scenarios: List[Dict[str, float]], threshold_km: float = 20.0) -> dict:
    if not route_geometry or not iceberg_scenarios:
        return {"min_km": 9999.0, "mean_km": 9999.0, "p90_km": 9999.0, "breached_threshold": False}
        
    route_coords = np.radians(np.array(route_geometry))
    r_lat, r_lon = route_coords[:, 0], route_coords[:, 1]
    
    min_distances = []
    
    for scene in iceberg_scenarios:
        i_lat, i_lon = np.radians(scene['lat']), np.radians(scene['lon'])
        dlat = r_lat - i_lat
        dlon = r_lon - i_lon
        a = np.sin(dlat/2.0)**2 + np.cos(r_lat)*np.cos(i_lat)*np.sin(dlon/2.0)**2
        c = 2 * np.arcsin(np.sqrt(a + 1e-10))
        distances_km = 6371.0 * c
        min_distances.append(np.min(distances_km))
        
    min_distances = np.array(min_distances)
    return {
        "min_km": float(np.min(min_distances)),
        "mean_km": float(np.mean(min_distances)),
        "p90_km": float(np.percentile(min_distances, 90)),
        "breached_threshold": bool(np.any(min_distances < threshold_km))
    }

def propagate_route_uncertainty(routes: List[Dict[str, Any]], hazard_field: np.ndarray, sic_result: Dict[str, Any], iceberg_result: Dict[str, Any], scenarios: int = 50) -> List[Dict[str, Any]]:
    logger.info(f"Propagating uncertainty for {len(routes)} routes over {scenarios} scenarios")
    
    mean_sic = sic_result.get('mean', np.zeros_like(hazard_field) if hazard_field is not None else np.zeros((10,10)))
    sigma_sic = sic_result.get('sigma', np.zeros_like(mean_sic))
    avg_sigma = np.nanmean(sigma_sic) if sigma_sic is not None and not np.isnan(np.nanmean(sigma_sic)) else 5.0
    
    ice_trajectories = iceberg_result.get("ensemble_trajectories", []) if iceberg_result else []
    iceberg_scenarios = []
    if ice_trajectories:
        for i in range(min(scenarios, len(ice_trajectories))):
            traj = ice_trajectories[i]
            iceberg_scenarios.append({'lat': traj['lats'][-1], 'lon': traj['lons'][-1]})
        while len(iceberg_scenarios) < scenarios:
            iceberg_scenarios.append(iceberg_scenarios[-1])
    else:
        iceberg_scenarios = [{'lat': 90.0, 'lon': 0.0} for _ in range(scenarios)] # Dummy far away

    updated_routes = []
    for route in routes:
        geom = route['geometry']
        base_max_sic = route.get('max_sic', 0.0)
        base_risk = route.get('expected_risk', 0.1)
        
        prox = compute_iceberg_proximity(geom, iceberg_scenarios, 20.0)
        
        feasible_count = 0
        scenario_risks = []
        
        for i in range(scenarios):
            scene_max_sic = base_max_sic + np.random.normal(0, avg_sigma)
            weather_mult = np.random.uniform(0.9, 1.1)
            scene_risk = base_risk * weather_mult
            
            is_feasible = True
            if scene_max_sic > 70.0:
                is_feasible = False
            if prox['breached_threshold']:
                is_feasible = False
                
            if is_feasible:
                feasible_count += 1
                
            scenario_risks.append(scene_risk)
            
        expected_risk = np.mean(scenario_risks)
        p90_risk = np.percentile(scenario_risks, 90)
        p95_risk = np.percentile(scenario_risks, 95)
        robust = feasible_count / scenarios
        
        updated_route = dict(route)
        updated_route['expected_risk'] = float(expected_risk)
        updated_route['p90_risk'] = float(p90_risk)
        updated_route['p95_risk'] = float(p95_risk)
        updated_route['robust_feasibility'] = float(robust)
        updated_route['feasibility_detail'] = f"{feasible_count} of {scenarios} scenarios"
        updated_route['scenarios_evaluated'] = scenarios
        
        updated_routes.append(updated_route)
        
    return updated_routes
