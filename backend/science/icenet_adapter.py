import os
import numpy as np
import xarray as xr
from typing import Dict, Any, Optional
from loguru import logger
from functools import lru_cache

@lru_cache(maxsize=1)
def load_sic_cache(cache_path: str = "data/cached/sic_forecast.nc") -> xr.Dataset:
    if not os.path.exists(cache_path):
        raise FileNotFoundError(f"SIC cache not found at {cache_path}")
    logger.info(f"Loading SIC cache from {cache_path}")
    return xr.open_dataset(cache_path)

def compute_ensemble_statistics(sic_ds: xr.Dataset, ensemble_size: int = 50) -> Dict[str, Any]:
    logger.info(f"Computing ensemble statistics (N={ensemble_size})")
    
    if 'ice_conc' not in sic_ds.data_vars:
        raise KeyError("Expected 'ice_conc' variable in dataset")
        
    sic_values = sic_ds['ice_conc'].values
    
    # Determine scale (0-1 or 0-100)
    max_val = np.nanmax(sic_values)
    upper_bound = 100.0 if max_val > 2.0 else 1.0
    
    # 5% of SIC value
    sigma = sic_values * 0.05
    
    valid_mask = ~np.isnan(sic_values)
    
    # Generate ensemble
    ensemble = np.full((ensemble_size,) + sic_values.shape, np.nan)
    
    for i in range(ensemble_size):
        noise = np.random.normal(loc=0, scale=sigma[valid_mask])
        member = np.copy(sic_values)
        member[valid_mask] = np.clip(member[valid_mask] + noise, 0, upper_bound)
        ensemble[i, valid_mask] = member[valid_mask]
        
    mean_val = np.nanmean(ensemble, axis=0)
    std_val = np.nanstd(ensemble, axis=0)
    q10 = mean_val
    q50 = mean_val
    q90 = mean_val
    
    if 'x' in sic_ds.coords and 'y' in sic_ds.coords:
        grid_x = sic_ds.x.values
        grid_y = sic_ds.y.values
    else:
        from pyproj import Transformer
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
        lon_arr = sic_ds['lon'].values if 'lon' in sic_ds.coords else sic_ds['longitude'].values
        lat_arr = sic_ds['lat'].values if 'lat' in sic_ds.coords else sic_ds['latitude'].values
        lon_mesh, lat_mesh = np.meshgrid(lon_arr, lat_arr)
        grid_x, grid_y = transformer.transform(lon_mesh, lat_mesh)
    
    # Get time safely
    valid_time = "current"
    if 'time' in sic_ds.coords and sic_ds.time.size > 0:
        time_val = sic_ds.time.values
        valid_time = str(time_val[0]) if time_val.ndim > 0 else str(time_val)
    
    return {
        'mean': mean_val,
        'sigma': std_val,
        'q10': q10,
        'q50': q50,
        'q90': q90,
        'grid': {'x': grid_x, 'y': grid_y, 'crs': 'EPSG:3031'},
        'valid_time': valid_time,
        'ensemble_size': ensemble_size,
        'source': 'OSI-SAF (observation-based baseline)',
        '_raw_ensemble': ensemble  # Private key for threshold calculation
    }

def compute_threshold_probability(sic_ds: xr.Dataset, threshold: float = 0.7) -> np.ndarray:
    logger.info(f"Computing threshold probability (P(SIC > {threshold}))")
    
    # Adjust threshold scale if dataset is 0-100
    sic_values = sic_ds['ice_conc'].values
    max_val = np.nanmax(sic_values)
    if max_val > 2.0 and threshold <= 1.0:
        threshold = threshold * 100.0
        
    stats = compute_ensemble_statistics(sic_ds)
    ensemble = stats['_raw_ensemble']
    
    with np.errstate(invalid='ignore'):
        exceeds = (ensemble > threshold)
    
    prob = np.nanmean(exceeds, axis=0)
    prob[np.isnan(sic_values)] = np.nan
    return prob

@lru_cache(maxsize=1)
def _forecast_sic_cached(threshold: float = 0.7):
    logger.info("Generating SIC forecast")
    ds = load_sic_cache()
    stats = compute_ensemble_statistics(ds)
    ensemble = stats.pop('_raw_ensemble')
    
    # Adjust threshold scale if dataset is 0-100
    sic_values = ds['ice_conc'].values
    max_val = np.nanmax(sic_values)
    if max_val > 2.0 and threshold <= 1.0:
        threshold = threshold * 100.0
        
    with np.errstate(invalid='ignore'):
        prob = np.nanmean(ensemble > threshold, axis=0)
    
    prob[np.isnan(sic_values)] = np.nan
    
    stats['prob_exceeds_threshold'] = prob
    stats['threshold_used'] = threshold
    
    return stats

def forecast_sic(region: Optional[Dict[str, float]] = None, threshold: float = 0.7) -> Dict[str, Any]:
    if region is None:
        return _forecast_sic_cached(threshold)
    
    logger.info("Generating SIC forecast for specific region")
    ds = load_sic_cache()
    
    lat_name = 'latitude' if 'latitude' in ds.coords else 'lat'
    lon_name = 'longitude' if 'longitude' in ds.coords else 'lon'
    
    # Sort coords to handle slicing direction
    lat_slice = slice(region.get('min_lat'), region.get('max_lat'))
    lon_slice = slice(region.get('min_lon'), region.get('max_lon'))
    
    if ds[lat_name][0] > ds[lat_name][-1]:
        lat_slice = slice(region.get('max_lat'), region.get('min_lat'))
    if ds[lon_name][0] > ds[lon_name][-1]:
        lon_slice = slice(region.get('max_lon'), region.get('min_lon'))
        
    ds = ds.sel({lat_name: lat_slice, lon_name: lon_slice})
        
    stats = compute_ensemble_statistics(ds)
    ensemble = stats.pop('_raw_ensemble')
    
    # Adjust threshold scale if dataset is 0-100
    sic_values = ds['ice_conc'].values
    max_val = np.nanmax(sic_values)
    if max_val > 2.0 and threshold <= 1.0:
        threshold = threshold * 100.0
        
    with np.errstate(invalid='ignore'):
        prob = np.nanmean(ensemble > threshold, axis=0)
    
    prob[np.isnan(sic_values)] = np.nan
    
    stats['prob_exceeds_threshold'] = prob
    stats['threshold_used'] = threshold
    
    return stats

def get_vessel_risk_field(vessel_sic_limit: float) -> np.ndarray:
    logger.info(f"Computing vessel risk field for limit: {vessel_sic_limit}")
    ds = load_sic_cache()
    return compute_threshold_probability(ds, threshold=vessel_sic_limit)
