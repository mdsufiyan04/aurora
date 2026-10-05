def validate_route_geometry(geometry, depth_grid, x, y, min_depth=15):
    """
    Check if route crosses land.
    Returns: (is_valid, num_land_crossings, samples)
    """
    from pyproj import Transformer
    import numpy as np
    
    transformer = Transformer.from_crs(
        "EPSG:4326", "EPSG:3031", always_xy=True
    )
    
    land_crossings = 0
    samples = []
    
    for i, (lat, lon) in enumerate(geometry):
        x_proj, y_proj = transformer.transform(lon, lat)
        
        # Find nearest grid cell
        xi = int(np.argmin(np.abs(x - x_proj)))
        yi = int(np.argmin(np.abs(y - y_proj)))
        
        depth = depth_grid[yi, xi]
        water_depth = -float(depth) if not np.isnan(depth) else -1000.0
        samples.append({
            "idx": i,
            "lat": lat,
            "lon": lon,
            "depth": float(depth),
            "is_land": bool(np.isnan(depth) or water_depth < min_depth),
        })
        
        if np.isnan(depth) or water_depth < min_depth:
            land_crossings += 1
    
    return land_crossings == 0, land_crossings, samples
