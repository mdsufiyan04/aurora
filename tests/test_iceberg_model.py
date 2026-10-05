import pytest
import time
import numpy as np
from backend.science.iceberg_model import (
    load_forcing,
    load_icebergs,
    interpolate_forcing,
    simulate_trajectory,
    simulate_ensemble,
    predict_iceberg_trajectory
)

def test_load_forcing():
    ds = load_forcing()
    assert 'uo' in ds.data_vars
    assert 'vo' in ds.data_vars
    assert 'u10' in ds.data_vars
    assert 'v10' in ds.data_vars

def test_load_icebergs():
    df = load_icebergs()
    # It might be empty if we only generated dummy netcdf, but testing it runs
    assert df is not None

def test_interpolate_forcing():
    ds = load_forcing()
    res = interpolate_forcing(ds, -69.4, 76.19, time=None)
    assert isinstance(res['uo'], float)
    assert isinstance(res['vo'], float)

def test_simulate_trajectory():
    ds = load_forcing()
    # Bharati station approx
    res = simulate_trajectory(-69.4, 76.19, "TEST_BERG", ds, horizon_hours=24)
    assert len(res['lat']) == 25
    
    lat_diff = abs(res['lat'][-1] - res['lat'][0])
    lon_diff = abs(res['lon'][-1] - res['lon'][0]) * np.cos(np.radians(-69.4))
    dist = np.sqrt(lat_diff**2 + lon_diff**2) * 111.32
    assert dist < 100.0

def test_simulate_ensemble():
    ds = load_forcing()
    t0 = time.time()
    res = simulate_ensemble(-69.4, 76.19, "TEST_BERG", ds, horizon_hours=120, ensemble_size=50)
    t1 = time.time()
    
    assert len(res['ensemble']) == 50
    assert (t1 - t0) < 5.0
    assert res['uncertainty']['p90']['lat'] >= res['uncertainty']['p50']['lat']

def test_predict_iceberg_trajectory():
    res = predict_iceberg_trajectory(start_lat=-69.4, start_lon=76.19)
    assert 'model' in res
    assert 'baseline' in res
