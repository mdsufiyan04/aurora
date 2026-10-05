import pytest
import time
import numpy as np
from backend.science.route_optimizer import (
    load_grid_data,
    build_hazard_field,
    build_cost_grid,
    astar_search,
    path_to_geometry,
    compute_route_metrics,
    optimize_route,
    optimize_multiple_routes,
    pareto_filter,
    DEFAULT_VESSEL,
    ROUTES
)

def test_load_grid_data():
    grid = load_grid_data()
    assert 'x' in grid
    assert 'depth' in grid
    assert grid['depth'].ndim == 2

def test_build_hazard_field():
    grid = load_grid_data()
    sic_res = {'prob_exceeds_threshold': np.zeros_like(grid['depth']), 'mean': np.zeros_like(grid['depth'])}
    ice_res = {'ensemble': [{'lat': [-69.4], 'lon': [76.19]}]}
    hf = build_hazard_field(sic_res, ice_res)
    assert hf.shape == grid['depth'].shape
    assert np.nanmin(hf) >= 0.0

def test_build_cost_grid():
    grid = load_grid_data()
    hf = np.zeros_like(grid['depth'])
    cg = build_cost_grid(grid, hf, DEFAULT_VESSEL, ROUTES['FASTEST'])
    assert cg.shape == grid['depth'].shape
    assert np.any(cg == np.inf)

def test_astar_search():
    cost_grid = np.ones((10, 10))
    cost_grid[1:9, 5] = np.inf
    path = astar_search(cost_grid, (1, 1), (8, 8))
    assert len(path) > 0

def test_path_to_geometry():
    grid = load_grid_data()
    path = [(0, 0), (1, 1)]
    geom = path_to_geometry(path, grid)
    assert len(geom) == 2
    assert isinstance(geom[0][0], float)

def test_compute_route_metrics():
    grid = load_grid_data()
    geom = [(-69.4, 76.19), (-69.5, 76.20)]
    path = [(0, 0), (1, 1)]
    hf = np.zeros_like(grid['depth'])
    metrics = compute_route_metrics(geom, path, hf, grid, DEFAULT_VESSEL)
    assert 'distance_km' in metrics
    assert 'fuel_tonnes' in metrics

def test_optimize_route():
    t0 = time.time()
    # Bharati to Maitri
    res = optimize_route(-69.0, 76.0, -69.5, 12.0)
    t1 = time.time()
    assert res.get('geometry') is not None
    assert (t1 - t0) < 15.0

def test_optimize_multiple_routes():
    res = optimize_multiple_routes(-69.0, 76.0, -69.5, 12.0)
    assert len(res) > 0

def test_pareto_filter():
    routes = [
        {'travel_time_hours': 10, 'fuel_tonnes': 10, 'expected_risk': 10}, 
        {'travel_time_hours': 20, 'fuel_tonnes': 20, 'expected_risk': 20},
        {'travel_time_hours': 30, 'fuel_tonnes': 5, 'expected_risk': 5}
    ]
    pareto = pareto_filter(routes)
    assert len(pareto) == 2
