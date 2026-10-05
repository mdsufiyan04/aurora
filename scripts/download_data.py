"""
Download scripts for AURORA data layer.
Fetches data from OSI-SAF, CMEMS, ERA5, BYU, and GEBCO.
"""
import os
import argparse
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
import copernicusmarine
from datetime import datetime, timezone, timedelta
import cdsapi
import requests
import zipfile
import io

load_dotenv()

# Map CMEMS variables to what the library explicitly expects
os.environ["COPERNICUSMARINE_USERNAME"] = os.getenv("CMEMS_USERNAME", "")
os.environ["COPERNICUSMARINE_PASSWORD"] = os.getenv("CMEMS_PASSWORD", "")

RAW_DIR = Path(os.getenv("DATA_RAW_DIR", "data/raw"))
RAW_DIR.mkdir(parents=True, exist_ok=True)

CMEMS_USER = os.getenv("CMEMS_USERNAME", "")
CMEMS_PASS = os.getenv("CMEMS_PASSWORD", "")

def download_osisaf_sic(force: bool = False):
    if (RAW_DIR / "osisaf_sic.nc").exists() and not force:
        logger.info("Skipping OSI-SAF SIC download, file exists.")
        return
        
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    logger.info(f"Downloading OSI-SAF SIC from {start_date} to {end_date}")
    
    try:
        copernicusmarine.subset(
            dataset_id="osisaf_obs-si_glo_phy-sic-south_nrt_amsr2_l4_P1D-m",
            variables=["ice_conc"],
            minimum_longitude=-20,
            maximum_longitude=90,
            minimum_latitude=-75,
            maximum_latitude=-65,
            start_datetime=start_date.strftime("%Y-%m-%dT%H:%M:%S"),
            end_datetime=end_date.strftime("%Y-%m-%dT%H:%M:%S"),
            output_filename=str(RAW_DIR / "osisaf_sic.nc"),
            force_download=force,
            username=CMEMS_USER,
            password=CMEMS_PASS,
        )
        logger.success("OSI-SAF SIC downloaded")
    except Exception as e:
        logger.error(f"OSI-SAF download failed: {e}")
        raise

def download_cmems_currents(force: bool = False):
    if (RAW_DIR / "cmems_currents.nc").exists() and not force:
        logger.info("Skipping CMEMS currents download, file exists.")
        return
        
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    logger.info(f"Downloading CMEMS currents from {start_date} to {end_date}")
    
    try:
        copernicusmarine.subset(
            dataset_id="cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m",
            variables=["uo", "vo"],
            minimum_longitude=-20,
            maximum_longitude=90,
            minimum_latitude=-75,
            maximum_latitude=-65,
            start_datetime=start_date.strftime("%Y-%m-%dT%H:%M:%S"),
            end_datetime=end_date.strftime("%Y-%m-%dT%H:%M:%S"),
            output_filename=str(RAW_DIR / "cmems_currents.nc"),
            force_download=force,
            username=CMEMS_USER,
            password=CMEMS_PASS,
        )
        logger.success("CMEMS currents downloaded")
    except Exception as e:
        logger.error(f"CMEMS download failed: {e}")
        raise

def download_era5(force: bool = False):
    if (RAW_DIR / "era5_weather.nc").exists() and not force:
        logger.info("Skipping ERA5 weather download, file exists.")
        return
        
    # 6-day delay for ERA5
    end_date = datetime.now(timezone.utc) - timedelta(days=6)
    start_date = end_date - timedelta(days=7)
    
    logger.info(f"Downloading ERA5 weather from {start_date} to {end_date}")
    
    days = []
    current = start_date
    while current <= end_date:
        days.append(current.strftime("%d"))
        current += timedelta(days=1)
    
    c = cdsapi.Client(
        url=os.getenv("CDSAPI_URL"),
        key=os.getenv("CDSAPI_KEY"),
    )
    
    try:
        c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": [
                    "10m_u_component_of_wind",
                    "10m_v_component_of_wind",
                    "mean_sea_level_pressure",
                    "surface_pressure",
                ],
                "year": str(end_date.year),
                "month": end_date.strftime("%m"),
                "day": list(set(days)),
                "time": ["00:00", "06:00", "12:00", "18:00"],
                "area": [-65, -20, -75, 90],
                "format": "netcdf",
            },
            str(RAW_DIR / "era5_weather.nc"),
        )
        logger.success("ERA5 weather downloaded")
    except Exception as e:
        logger.error(f"ERA5 download failed: {e}")
        raise

def download_byu_icebergs(force: bool = False):
    # Just check if directory exists this time since we download to zip
    if (RAW_DIR / "updated7_consol").exists() and not force:
        logger.info("Skipping BYU iceberg database download, files exist.")
        return
        
    logger.info("Downloading BYU iceberg database ZIP")
    url = "https://www.scp.byu.edu/data/iceberg/consolidated_database_v8.0.zip"
    
    try:
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(RAW_DIR)
        logger.success(f"BYU icebergs extracted to {RAW_DIR}")
    except Exception as e:
        logger.error(f"BYU download failed: {e}")
        raise

def download_gebco(force: bool = False):
    logger.info("GEBCO bathymetry — attempting download")
    logger.warning(
        "GEBCO download requires manual step. "
        "Visit https://download.gebco.net/ and download "
        "region: -75 to -65 lat, -20 to 90 lon"
    )
    logger.info("Place downloaded GEBCO file at data/raw/gebco_bathymetry.nc")

def main():
    parser = argparse.ArgumentParser(description="Download data for AURORA")
    parser.add_argument("--force", action="store_true", help="Force redownload of all files")
    parser.add_argument(
        "--only",
        choices=["osisaf", "cmems", "era5", "byu", "gebco"],
        help="Download only a specific dataset"
    )
    args = parser.parse_args()

    downloads = {
        "osisaf": download_osisaf_sic,
        "cmems": download_cmems_currents,
        "era5": download_era5,
        "byu": download_byu_icebergs,
        "gebco": download_gebco,
    }

    if args.only:
        downloads[args.only](args.force)
    else:
        for func in downloads.values():
            try:
                func(args.force)
            except Exception as e:
                logger.error(f"Failed to run download {func.__name__}: {e}")

if __name__ == "__main__":
    main()
