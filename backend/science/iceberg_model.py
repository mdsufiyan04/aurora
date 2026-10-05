import os
import glob
import numpy as np
import pandas as pd
import xarray as xr
from typing import Dict, Any, Optional
from loguru import logger
from functools import lru_cache
from pyproj import Transformer
from scipy.interpolate import RegularGridInterpolator

@lru_cache(maxsize=1)
def load_forcing(cache_path: str = "data/cached/forcing.nc") -> xr.Dataset:
    if not os.path.exists(cache_path):
        raise FileNotFoundError(f"Forcing cache not found at {cache_path}")
    logger.info(f"Loading forcing cache from {cache_path}")
    return xr.open_dataset(cache_path)

@lru_cache(maxsize=1)
def get_interpolators(cache_path: str = "data/cached/forcing.nc"):
    """Cache the scipy RegularGridInterpolators for speed."""
    ds = load_forcing(cache_path)
    
    y = ds['y'].values if 'y' in ds.coords else ds['lat'].values
    x = ds['x'].values if 'x' in ds.coords else ds['lon'].values
    
    y_asc = np.argsort(y)
    x_asc = np.argsort(x)
    y_sorted = y[y_asc]
    x_sorted = x[x_asc]
    
    interpolators = {}
    
    for var in ['uo', 'vo', 'u10', 'v10']:
        if var in ds.data_vars:
            val = ds[var].values
            if val.ndim == 3:
                val = np.nanmean(val, axis=0)
            elif val.ndim == 4:
                val = np.nanmean(val, axis=(0, 1))
                
            val_sorted = val[y_asc, :]
            val_sorted = val_sorted[:, x_asc]
            val_sorted = np.nan_to_num(val_sorted, nan=0.0)
            
            interpolators[var] = RegularGridInterpolator(
                (y_sorted, x_sorted), val_sorted, 
                bounds_error=False, fill_value=0.0
            )
            
    return interpolators

def interpolate_forcing(forcing_ds: xr.Dataset, lat: float, lon: float, time: Any = None) -> Dict[str, float]:
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
    x, y = transformer.transform(lon, lat)
    
    interpolators = get_interpolators()
    
    res = {}
    for var in ['uo', 'vo', 'u10', 'v10']:
        if var in interpolators:
            res[var] = float(interpolators[var]((y, x)))
        else:
            res[var] = 0.0
            
    return res

def load_icebergs(csv_dir: str = "data/raw/updated7_consol") -> pd.DataFrame:
    if not os.path.exists(csv_dir):
        logger.warning(f"Iceberg directory not found: {csv_dir}")
        return pd.DataFrame()
        
    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    if not csv_files:
        logger.warning(f"No CSV files found in {csv_dir}")
        return pd.DataFrame()
        
    dfs = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
        except Exception as e:
            logger.error(f"Error reading {f}: {e}")
            
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

def simulate_trajectory(start_lat: float, start_lon: float, iceberg_id: str, forcing_ds: xr.Dataset, 
                       horizon_hours: int = 120, dt_hours: int = 1, wind_factor: float = 0.02) -> Dict[str, Any]:
    
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
    interpolators = get_interpolators()
    
    times = [0]
    lats = [start_lat]
    lons = [start_lon]
    dt_seconds = dt_hours * 3600
    
    cur_lat, cur_lon = start_lat, start_lon
    
    for t in range(dt_hours, horizon_hours + 1, dt_hours):
        x, y = transformer.transform(cur_lon, cur_lat)
        pts = np.array([[y, x]])
        
        uo = float(interpolators['uo'](pts)[0]) if 'uo' in interpolators else 0.0
        vo = float(interpolators['vo'](pts)[0]) if 'vo' in interpolators else 0.0
        u10 = float(interpolators['u10'](pts)[0]) if 'u10' in interpolators else 0.0
        v10 = float(interpolators['v10'](pts)[0]) if 'v10' in interpolators else 0.0
        
        u_berg = uo + wind_factor * u10
        v_berg = vo + wind_factor * v10
        
        lat_rad = np.radians(cur_lat)
        cos_lat = np.cos(lat_rad)
        if abs(cos_lat) < 1e-6:
            cos_lat = 1e-6 * np.sign(cos_lat) if cos_lat != 0 else 1e-6
            
        cur_lat += (v_berg * dt_seconds) / 111320.0
        cur_lon += (u_berg * dt_seconds) / (111320.0 * cos_lat)
        
        times.append(t)
        lats.append(cur_lat)
        lons.append(cur_lon)
        
    return {'times': times, 'lat': lats, 'lon': lons}

def simulate_ensemble(start_lat: float, start_lon: float, iceberg_id: str, forcing_ds: xr.Dataset,
                     horizon_hours: int = 120, ensemble_size: int = 50) -> Dict[str, Any]:
    logger.info(f"Simulating {ensemble_size}-member ensemble for iceberg {iceberg_id}")
    
    baseline = simulate_trajectory(start_lat, start_lon, iceberg_id, forcing_ds, horizon_hours=horizon_hours)
    
    dt_hours = 1
    dt_seconds = 3600
    steps = horizon_hours // dt_hours
    
    # Perturb initial position: ±2 km Gaussian
    lat_noise = np.random.normal(0, 2000 / 111320.0, ensemble_size)
    lon_noise = np.random.normal(0, 2000 / (111320.0 * np.cos(np.radians(start_lat))), ensemble_size)
    
    cur_lats = start_lat + lat_noise
    cur_lons = start_lon + lon_noise
    
    # Perturb wind factor: ±0.005 Gaussian around 0.02
    wind_factors = np.random.normal(0.02, 0.005, ensemble_size)
    current_multipliers = np.random.normal(1.0, 0.05, ensemble_size)
    
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
    interpolators = get_interpolators()
    
    ensemble_lats = np.zeros((ensemble_size, steps + 1))
    ensemble_lons = np.zeros((ensemble_size, steps + 1))
    
    ensemble_lats[:, 0] = cur_lats
    ensemble_lons[:, 0] = cur_lons
    
    for t_idx in range(1, steps + 1):
        x, y = transformer.transform(cur_lons, cur_lats)
        pts = np.column_stack((y, x))
        
        uo = interpolators['uo'](pts) if 'uo' in interpolators else np.zeros(ensemble_size)
        vo = interpolators['vo'](pts) if 'vo' in interpolators else np.zeros(ensemble_size)
        u10 = interpolators['u10'](pts) if 'u10' in interpolators else np.zeros(ensemble_size)
        v10 = interpolators['v10'](pts) if 'v10' in interpolators else np.zeros(ensemble_size)
        
        uo *= current_multipliers
        vo *= current_multipliers
        
        u_berg = uo + wind_factors * u10
        v_berg = vo + wind_factors * v10
        
        cos_lat = np.cos(np.radians(cur_lats))
        cos_lat[np.abs(cos_lat) < 1e-6] = 1e-6
        
        cur_lats += (v_berg * dt_seconds) / 111320.0
        cur_lons += (u_berg * dt_seconds) / (111320.0 * cos_lat)
        
        ensemble_lats[:, t_idx] = cur_lats
        ensemble_lons[:, t_idx] = cur_lons
        
    members = [{'lat': ensemble_lats[i].tolist(), 'lon': ensemble_lons[i].tolist()} for i in range(ensemble_size)]
    
    final_lats = ensemble_lats[:, -1]
    final_lons = ensemble_lons[:, -1]
    
    return {
        'baseline': baseline,
        'ensemble': members,
        'uncertainty': {
            'p50': {'lat': float(np.percentile(final_lats, 50)), 'lon': float(np.percentile(final_lons, 50))},
            'p90': {'lat': float(np.percentile(final_lats, 90)), 'lon': float(np.percentile(final_lons, 90))},
            'p95': {'lat': float(np.percentile(final_lats, 95)), 'lon': float(np.percentile(final_lons, 95))}
        },
        'current_position': {'lat': float(start_lat), 'lon': float(start_lon)},
        'model': 'Bigg-style physics (2% wind factor)',
        'parameters': {'wind_factor': 0.02, 'dt_hours': 1}
    }

def predict_iceberg_trajectory(iceberg_id: Optional[str] = None, start_lat: Optional[float] = None, 
                              start_lon: Optional[float] = None, horizon_hours: int = 120) -> Dict[str, Any]:
    ds = load_forcing()
    if start_lat is None or start_lon is None:
        start_lat, start_lon = -69.4, 76.19
    return simulate_ensemble(start_lat, start_lon, iceberg_id or "UNKNOWN", ds, horizon_hours=horizon_hours)
