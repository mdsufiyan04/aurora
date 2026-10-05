import pytest
import numpy as np
import xarray as xr
from backend.science.icenet_adapter import (
    load_sic_cache,
    compute_ensemble_statistics,
    compute_threshold_probability,
    forecast_sic
)

def test_load_sic_cache():
    ds = load_sic_cache("data/cached/sic_forecast.nc")
    assert isinstance(ds, xr.Dataset)
    assert 'ice_conc' in ds.data_vars

def test_compute_statistics():
    ds = load_sic_cache("data/cached/sic_forecast.nc")
    # Small ensemble size for fast testing
    stats = compute_ensemble_statistics(ds, ensemble_size=10)
    
    assert 'mean' in stats
    assert 'sigma' in stats
    assert 'q10' in stats
    assert 'q50' in stats
    assert 'q90' in stats
    assert 'grid' in stats
    assert 'valid_time' in stats
    assert 'ensemble_size' in stats
    assert 'source' in stats
    
    assert stats['mean'].ndim == 2
    assert stats['ensemble_size'] == 10

def test_threshold_probability():
    ds = load_sic_cache("data/cached/sic_forecast.nc")
    prob = compute_threshold_probability(ds, threshold=0.7)
    assert prob.ndim == 2
    # Probability must be in [0, 1] (or nan)
    valid_probs = prob[~np.isnan(prob)]
    if len(valid_probs) > 0:
        assert np.min(valid_probs) >= 0.0
        assert np.max(valid_probs) <= 1.0

def test_forecast_sic():
    stats = forecast_sic(threshold=0.7)
    assert 'prob_exceeds_threshold' in stats
    assert stats['prob_exceeds_threshold'].shape == stats['mean'].shape
