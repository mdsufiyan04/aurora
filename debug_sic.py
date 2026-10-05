import xarray as xr
import numpy as np

print("=" * 60)
print("RAW SIC FILE INSPECTION")
print("=" * 60)

ds = xr.open_dataset("data/cached/sic_forecast.nc")
print(f"Variables: {list(ds.data_vars)}")
print(f"Dimensions: {dict(ds.dims)}")
print(f"Coordinates: {list(ds.coords)}")

if 'ice_conc' in ds.data_vars:
    sic = ds['ice_conc']
    print(f"\nice_conc shape: {sic.shape}")
    print(f"ice_conc min: {float(np.nanmin(sic.values))}")
    print(f"ice_conc max: {float(np.nanmax(sic.values))}")
    print(f"ice_conc mean: {float(np.nanmean(sic.values))}")
    print(f"Non-NaN count: {int(sic.notnull().sum())}")
    print(f"Total count: {sic.size}")
    print(f"NaN percentage: {100 * (1 - sic.notnull().sum() / sic.size):.1f}%")
    print(f"\nSample values (first 10 flattened):")
    print(sic.values.flatten()[:10])
    
    # Check if it's a range/normalization issue
    print(f"\nAfter normalization checks:")
    print(f"Values > 1: {(sic.values > 1).sum()}")
    print(f"Values > 100: {(sic.values > 100).sum()}")
    print(f"Values between 0-1: {((sic.values >= 0) & (sic.values <= 1)).sum()}")
    print(f"Values between 0-100: {((sic.values >= 0) & (sic.values <= 100)).sum()}")
else:
    print("ice_conc variable NOT FOUND")

print()
print("=" * 60)
print("AFTER adapter processing")
print("=" * 60)
from backend.science.icenet_adapter import load_sic_cache, forecast_sic
ds2 = load_sic_cache()
print(f"Loaded dims: {dict(ds2.dims)}")

# Check if the adapter is applying a mask
mask = ds2['ice_conc'].notnull()
print(f"Non-NaN after adapter: {mask.sum().item()}")
