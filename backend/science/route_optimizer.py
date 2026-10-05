import os
import heapq
import time
import math
import numpy as np
import xarray as xr
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
from functools import lru_cache
from pyproj import Transformer
from scipy.ndimage import zoom
from scipy.interpolate import RegularGridInterpolator
from backend.science.icenet_adapter import forecast_sic
from backend.science.iceberg_model import predict_iceberg_trajectory

def interpolate_to_grid(source_2d, source_x, source_y, 
                        target_x, target_y):
    """
    Interpolate a 2D array to a target grid using ACTUAL 
    coordinates (not index-based stretching).
    
    source_2d: (ny, nx) array
    source_x:  (nx,) array of x coords (EPSG:3031 meters)
    source_y:  (ny,) array of y coords (EPSG:3031 meters)
    target_x:  (nx_target,) or (ny_target, nx_target) array
    target_y:  (ny_target,) or (ny_target, nx_target) array
    """
    if source_y[0] > source_y[-1]:
        source_y = source_y[::-1]
        source_2d = source_2d[::-1, :]
        
    if source_x[0] > source_x[-1]:
        source_x = source_x[::-1]
        source_2d = source_2d[:, ::-1]

    # Build interpolator in (y, x) order for numpy
    interp = RegularGridInterpolator(
        (source_y, source_x),
        source_2d,
        method='nearest',
        bounds_error=False,
        fill_value=np.nan
    )
    
    # Handle 1D target coords
    if target_x.ndim == 1 and target_y.ndim == 1:
        target_x, target_y = np.meshgrid(target_x, target_y)
    
    # Stack points for interpolator: (N, 2) with [y, x] order
    points = np.stack([target_y.ravel(), target_x.ravel()], axis=-1)
    
    result = interp(points).reshape(target_y.shape)
    return result

DEFAULT_VESSEL = {
  "name": "SDA",
  "max_speed_knots": 15.0,
  "cruise_speed_knots": 12.0,
  "min_depth_m": 15.0,
  "max_sic": 1.0,
  "max_wave_m": 4.0,
  "fuel_rate_kg_per_km": 45.0
}

ROUTES = {
    'FASTEST':        {'w_time': 1.0, 'w_fuel': 0.0, 'w_sic': 0.0, 'w_iceberg': 0.0, 'w_weather': 0.0},
    'SAFEST':         {'w_time': 0.0, 'w_fuel': 0.0, 'w_sic': 0.7, 'w_iceberg': 0.3, 'w_weather': 0.0},
    'FUEL-EFFICIENT': {'w_time': 0.0, 'w_fuel': 1.0, 'w_sic': 0.0, 'w_iceberg': 0.0, 'w_weather': 0.0},
    'BALANCED':       {'w_time': 0.5, 'w_fuel': 0.0, 'w_sic': 0.35, 'w_iceberg': 0.15, 'w_weather': 0.0}
}

@lru_cache(maxsize=1)
def load_grid_data() -> Dict[str, Any]:
    logger.info("Loading and aligning grid data...")
    forcing = xr.open_dataset("data/cached/forcing.nc")
    sic = xr.open_dataset("data/cached/sic_forecast.nc")
    bathy = xr.open_dataset("data/cached/bathymetry.nc")
    
    # Align grids to forcing layout using nearest neighbor for speed
    bathy_aligned = bathy.interp_like(forcing, method='nearest')
    
    x = forcing['x'].values if 'x' in forcing.coords else forcing['lon'].values
    y = forcing['y'].values if 'y' in forcing.coords else forcing['lat'].values
    
    depth = bathy_aligned['elevation'].values if 'elevation' in bathy_aligned.data_vars else np.zeros_like(forcing['uo'].values)
    
    if 'ice_conc' in sic.data_vars:
        sic_x = sic['x'].values if 'x' in sic.coords else sic['lon'].values
        sic_y = sic['y'].values if 'y' in sic.coords else sic['lat'].values
        ice_conc = interpolate_to_grid(sic['ice_conc'].values, sic_x, sic_y, x, y)
    else:
        ice_conc = np.zeros_like(forcing['uo'].values)
    
    u10 = np.nanmean(forcing['u10'].values, axis=0) if forcing['u10'].ndim > 2 else forcing['u10'].values
    v10 = np.nanmean(forcing['v10'].values, axis=0) if forcing['v10'].ndim > 2 else forcing['v10'].values
    uo = np.nanmean(forcing['uo'].values, axis=0) if forcing['uo'].ndim > 2 else forcing['uo'].values
    vo = np.nanmean(forcing['vo'].values, axis=0) if forcing['vo'].ndim > 2 else forcing['vo'].values
    
    return {
        'x': x,
        'y': y,
        'depth': depth,
        'sic': ice_conc,
        'wind_speed': np.sqrt(u10**2 + v10**2),
        'current_speed': np.sqrt(uo**2 + vo**2)
    }

def build_hazard_field(sic_adapter_result: Dict[str, Any], iceberg_ensemble: Dict[str, Any]) -> np.ndarray:
    sic_prob = sic_adapter_result.get('prob_exceeds_threshold', None)
    if sic_prob is None:
        sic_prob = np.zeros(sic_adapter_result['mean'].shape)
        
    grid_data = load_grid_data()
    x = grid_data['x']
    y = grid_data['y']
    
    target_shape = (len(y), len(x))
    
    sic_grid = sic_adapter_result.get('grid', {})
    if sic_grid and 'x' in sic_grid and 'y' in sic_grid:
        sic_x = np.array(sic_grid['x'])
        sic_y = np.array(sic_grid['y'])
        sic_prob = interpolate_to_grid(
            sic_prob, sic_x, sic_y, x, y
        )
    else:
        logger.warning("SIC grid coords missing; assuming same as route grid")
        if sic_prob.shape != target_shape:
            zoom_y = target_shape[0] / sic_prob.shape[0]
            zoom_x = target_shape[1] / sic_prob.shape[1]
            sic_prob = zoom(sic_prob, (zoom_y, zoom_x), order=0)
    
    iceberg_hazard = np.zeros((len(y), len(x)))
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
    
    members = iceberg_ensemble.get('ensemble', [])
    for member in members:
        for lat, lon in zip(member['lat'], member['lon']):
            ix, iy = transformer.transform(lon, lat)
            x_idx = np.searchsorted(x, ix) - 1
            y_idx = np.searchsorted(y, iy) - 1
            if 0 <= x_idx < len(x) and 0 <= y_idx < len(y):
                iceberg_hazard[y_idx, x_idx] += 1
                
    if len(members) > 0:
        iceberg_hazard = iceberg_hazard / (len(members) * len(members[0]['lat']))
        
    max_hz = np.max(iceberg_hazard)
    if max_hz > 0:
        iceberg_hazard = iceberg_hazard / max_hz
        
    hazard = 0.5 * sic_prob + 0.5 * iceberg_hazard
    
    max_h = np.nanmax(hazard)
    if max_h > 0:
        hazard = hazard / max_h
    return np.nan_to_num(hazard, 0.0)

def build_cost_grid(grid_data: Dict[str, Any], hazard_field: np.ndarray, vessel: Dict[str, Any], weights: Dict[str, float]) -> np.ndarray:
    depth = grid_data['depth']
    sic = grid_data['sic']
    wind = grid_data['wind_speed']
    
    cost = np.ones_like(depth) * 0.1
    
    wind_filled = np.nan_to_num(wind, nan=0.0)
    sic_filled = np.nan_to_num(sic, nan=0.0)
    
    cost += weights.get('w_time', 0) * 1.0
    cost += weights.get('w_fuel', 0) * 1.0
    cost += weights.get('w_sic', 0) * hazard_field
    cost += weights.get('w_iceberg', 0) * hazard_field
    cost += weights.get('w_weather', 0) * (wind_filled / (np.max(wind_filled) + 1e-6))
    
    # GEBCO bathymetry is negative for oceans, so -elevation is water depth
    # NaN values indicate land/ice-shelf in this dataset, which should be blocked.
    water_depth = -np.nan_to_num(depth, nan=1000.0)
    cost[water_depth < vessel.get('min_depth_m', 15.0)] = np.inf
    
    # Check max SIC
    sic_norm = sic_filled / 100.0 if np.max(sic_filled) > 2.0 else sic_filled
    cost[sic_norm > vessel.get('max_sic', 1.0)] = np.inf
    
    # Check max wave (proxy via wind)
    cost[wind_filled > 20.0] = np.inf
    
    return cost

def astar_search(cost_grid: np.ndarray, start_xy: Tuple[int, int], goal_xy: Tuple[int, int]) -> List[Tuple[int, int]]:
    ny, nx = cost_grid.shape
    logger.info(f"Unblocked cells: {np.sum(cost_grid != np.inf)} / {cost_grid.size}")
    
    if cost_grid[start_xy[1], start_xy[0]] == np.inf:
        logger.warning("Start point is blocked! Route may fail.")
    if cost_grid[goal_xy[1], goal_xy[0]] == np.inf:
        logger.warning("Goal point is blocked! Route may fail.")
        
    def heuristic(a, b):
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2) * 2.0
        
    open_set = []
    heapq.heappush(open_set, (0, start_xy))
    
    came_from = {}
    g_score = {start_xy: 0}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == goal_xy:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_xy)
            path.reverse()
            return path
            
        x, y = current
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
            nx_pos, ny_pos = x + dx, y + dy
            if 0 <= nx_pos < nx and 0 <= ny_pos < ny:
                step_cost = cost_grid[ny_pos, nx_pos]
                if step_cost == np.inf:
                    continue
                    
                dist = 1.414 if dx != 0 and dy != 0 else 1.0
                tentative_g = g_score[current] + step_cost * dist
                
                neighbor = (nx_pos, ny_pos)
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal_xy)
                    heapq.heappush(open_set, (f_score, neighbor))
                    
    logger.warning("No path found.")
    return []

def path_to_geometry(path: List[Tuple[int, int]], grid_data: Dict[str, Any]) -> List[Tuple[float, float]]:
    if not path:
        return []
    
    x = grid_data['x']
    y = grid_data['y']
    transformer = Transformer.from_crs("EPSG:3031", "EPSG:4326", always_xy=True)
    
    geom = []
    for px, py in path:
        px = max(0, min(px, len(x)-1))
        py = max(0, min(py, len(y)-1))
        lon, lat = transformer.transform(x[px], y[py])
        geom.append((float(lat), float(lon)))
        
    return geom

def compute_route_metrics(geometry: List[Tuple[float, float]], path_indices: List[Tuple[int, int]], hazard_field: np.ndarray, grid_data: Dict[str, Any], vessel: Dict[str, Any]) -> Dict[str, Any]:
    if not geometry or not path_indices:
        return {}
        
    dist_km = 0.0
    for i in range(1, len(geometry)):
        lat1, lon1 = geometry[i-1]
        lat2, lon2 = geometry[i]
        
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        dist_km += R * c
        
    cruise = vessel.get('cruise_speed_knots', 12.0) * 1.852
    travel_time = dist_km / cruise if cruise > 0 else 0
    fuel = dist_km * vessel.get('fuel_rate_kg_per_km', 45.0) / 1000.0
    
    risk_values = [hazard_field[ny, nx] for nx, ny in path_indices]
    expected_risk = float(np.mean(risk_values)) if risk_values else 0.0
    max_risk = float(np.max(risk_values)) if risk_values else 0.0
    p90_risk = float(np.percentile(risk_values, 90)) if risk_values else 0.0
    ice_hours = sum(1 for r in risk_values if r > 0.5)
    
    sic_grid = grid_data['sic']
    sic_values = [sic_grid[ny, nx] for nx, ny in path_indices]
    sic_values = np.nan_to_num(sic_values, nan=0.0)
    max_sic = float(np.max(sic_values)) if len(sic_values) > 0 else 0.0
    mean_sic = float(np.mean(sic_values)) if len(sic_values) > 0 else 0.0
    
    return {
        'distance_km': float(dist_km),
        'travel_time_hours': float(travel_time),
        'fuel_tonnes': float(fuel),
        'max_sic_encountered': max_sic,
        'mean_sic': mean_sic,
        'expected_risk': expected_risk,
        'max_risk': max_risk,
        'p90_risk': p90_risk,
        'ice_hours': ice_hours
    }

def optimize_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float,
                   hazard: np.ndarray, grid: Dict[str, Any],
                   vessel: Dict[str, Any] = None, weights: Dict[str, float] = None) -> Dict[str, Any]:
    
    vessel = vessel or DEFAULT_VESSEL
    weights = weights or ROUTES['BALANCED']
    
    cost_grid = build_cost_grid(grid, hazard, vessel, weights)
    
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
    sx, sy = transformer.transform(start_lon, start_lat)
    ex, ey = transformer.transform(end_lon, end_lat)
    
    sx_idx = int(np.argmin(np.abs(grid['x'] - sx)))
    sy_idx = int(np.argmin(np.abs(grid['y'] - sy)))
    ex_idx = int(np.argmin(np.abs(grid['x'] - ex)))
    ey_idx = int(np.argmin(np.abs(grid['y'] - ey)))
    
    def find_nearest_unblocked(x_idx, y_idx, cg):
        if cg[y_idx, x_idx] != np.inf:
            return (x_idx, y_idx)
        for r in range(1, max(cg.shape)):
            for dx in range(-r, r+1):
                for dy in range(-r, r+1):
                    nx, ny = x_idx+dx, y_idx+dy
                    if 0 <= nx < cg.shape[1] and 0 <= ny < cg.shape[0]:
                        if cg[ny, nx] != np.inf:
                            return (nx, ny)
        return (x_idx, y_idx)
        
    start_xy = find_nearest_unblocked(sx_idx, sy_idx, cost_grid)
    goal_xy = find_nearest_unblocked(ex_idx, ey_idx, cost_grid)
    
    path = astar_search(cost_grid, start_xy, goal_xy)
    
    geom = path_to_geometry(path, grid)
    metrics = compute_route_metrics(geom, path, hazard, grid, vessel)
    
    metrics['geometry'] = geom
    return metrics

def optimize_multiple_routes(start_lat: float, start_lon: float, end_lat: float, end_lon: float,
                             hazard: np.ndarray, grid: Dict[str, Any],
                             vessel: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    results = []
    for label, w in ROUTES.items():
        res = optimize_route(start_lat, start_lon, end_lat, end_lon, hazard, grid, vessel, w)
        if res.get('geometry'):
            res['label'] = label
            results.append(res)
        else:
            logger.warning(f"Route {label} failed to find a path.")
            
    unique_routes = []
    seen = []
    for r in results:
        dist = r['distance_km']
        is_dup = any(abs(dist - s) < 1.0 for s in seen)
        if not is_dup:
            unique_routes.append(r)
            seen.append(dist)
            
    return unique_routes

def pareto_filter(routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Disabled strict pareto filtering to ensure all requested UI configs are displayed
    # as A* suboptimality can cause valid trade-offs to appear dominated.
    return routes
