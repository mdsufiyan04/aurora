from backend.science.route_optimizer import (
    load_grid_data, build_hazard_field, build_cost_grid,
    astar_search, path_to_geometry, compute_route_metrics,
    optimize_multiple_routes, pareto_filter
)
from backend.science.icenet_adapter import forecast_sic
from backend.science.iceberg_model import predict_iceberg_trajectory
import numpy as np

sic = forecast_sic(threshold=0.7)
berg = predict_iceberg_trajectory(start_lat=-69.4, start_lon=76.2)
hazard = build_hazard_field(sic, berg)

print("=" * 60)
print("MULTIPLE ROUTES")
print("=" * 60)

routes = optimize_multiple_routes(
    start_lat=-69.4, start_lon=76.2,
    end_lat=-70.7, end_lon=11.7,
    hazard=hazard,
    grid=load_grid_data()
)

print(f"Total routes returned: {len(routes)}")
for r in routes:
    print(f"\n[{r['label']}]")
    print(f"  Distance: {r['distance_km']:.1f} km")
    print(f"  Expected risk: {r.get('expected_risk', 'MISSING')}")
    print(f"  Max SIC: {r.get('max_sic_encountered', 'MISSING')}")
    print(f"  Geometry length: {len(r.get('geometry', []))}")
    print(f"  First coord: {r['geometry'][0] if r.get('geometry') else 'EMPTY'}")
    print(f"  Last coord: {r['geometry'][-1] if r.get('geometry') else 'EMPTY'}")

print("\n" + "=" * 60)
print("MEAN HAZARD EXPOSURE")
print("=" * 60)
from pyproj import Transformer
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
grid = load_grid_data()
grid_x = grid['x']
grid_y = grid['y']
for r in routes:
    path = r.get('geometry', [])
    hazards_on_path = []
    for lat, lon in path:
        px, py = transformer.transform(lon, lat)
        idx_x = np.argmin(np.abs(grid_x - px))
        idx_y = np.argmin(np.abs(grid_y - py))
        hazards_on_path.append(hazard[idx_y, idx_x])
    mean_haz = np.mean(hazards_on_path) if hazards_on_path else 0.0
    print(f"{r['label']}: mean hazard = {mean_haz:.4f}")

print()
print("=" * 60)
print("PARETO FILTER")
print("=" * 60)
pareto = pareto_filter(routes)
print(f"Pareto routes: {len(pareto)}")
for r in pareto:
    print(f"  [{r['label']}] risk={r.get('expected_risk')}, dist={r['distance_km']:.1f}")

print("\n" + "=" * 60)
print("ROUTE VALIDATOR")
print("=" * 60)
from backend.science.route_validator import validate_route_geometry

depth_grid = grid['depth']
x = grid['x']
y = grid['y']

for route in routes:
    is_valid, crossings, samples = validate_route_geometry(
        route['geometry'], depth_grid, x, y
    )
    print(f"{route['label']}: valid={is_valid}, land_crossings={crossings}/{len(samples)}")
    if not is_valid:
        # Print first 5 land crossings
        land_samples = [s for s in samples if s['is_land']][:5]
        for s in land_samples:
            print(f"  Step {s['idx']}: lat={s['lat']:.2f} lon={s['lon']:.2f} depth={s['depth']:.1f}")
