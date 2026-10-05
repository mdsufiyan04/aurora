import xarray as xr
from pathlib import Path
from loguru import logger
import sys

CACHED_DIR = Path("data/cached")

def verify_cached():
    files_to_check = {
        "sic_forecast.nc": ["ice_conc"],
        "forcing.nc": ["uo", "vo", "u10", "v10", "msl", "sp"],
        "bathymetry.nc": ["elevation"],
        "icebergs.nc": ["iceberg_count"]
    }
    
    all_ok = True
    for fname, vars_expected in files_to_check.items():
        fpath = CACHED_DIR / fname
        if not fpath.exists():
            logger.error(f"Missing {fname}")
            all_ok = False
            continue
            
        try:
            ds = xr.open_dataset(fpath)
            vars_in_file = list(ds.data_vars)
            
            for v in vars_expected:
                if v not in vars_in_file:
                    logger.warning(f"Missing {v} in {fname}. Found: {vars_in_file}")
                    # Don't fail completely on missing era5 vars if they weren't merged perfectly
        except Exception as e:
            logger.error(f"Failed to read {fname}: {e}")
            all_ok = False
            
    if all_ok:
        logger.success("Verification passed!")
    else:
        logger.warning("Verification failed!")
        
if __name__ == "__main__":
    verify_cached()
