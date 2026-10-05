# AURORA Data Contract

This document defines the data foundation for the Antarctic Navigation Decision Support System.

## Cached Files Specification

### `sic_forecast.nc`
- **Variable names:** `sea_ice_area_fraction`
- **Units:** Percentage (0-100) or fraction (0-1)
- **Spatial CRS:** EPSG:3031 (Antarctic Polar Stereographic)
- **Spatial resolution:** 0.1°
- **Temporal resolution:** Daily
- **Time coverage:** Last 30 days
- **Data source:** OSI-SAF
- **Data latency:** Near Real-Time (NRT)
- **Missing data handling:** `NaN`
- **Checksum algorithm:** SHA-256

### `icebergs.nc`
- **Variable names:** `latitude`, `longitude`, `iceberg_id`, `size`
- **Units:** Degrees (unprojected), meters (size)
- **Spatial CRS:** EPSG:3031 (Antarctic Polar Stereographic)
- **Spatial resolution:** 0.1°
- **Temporal resolution:** Daily
- **Time coverage:** Last 30 days
- **Data source:** BYU/NIC
- **Data latency:** Daily
- **Missing data handling:** `NaN`
- **Checksum algorithm:** SHA-256

### `forcing.nc`
- **Variable names:** `10m_u_component_of_wind`, `10m_v_component_of_wind`, `mean_sea_level_pressure`, `surface_pressure`, `uo`, `vo`
- **Units:** m/s (wind/current), Pa (pressure)
- **Spatial CRS:** EPSG:3031 (Antarctic Polar Stereographic)
- **Spatial resolution:** 0.1°
- **Temporal resolution:** Hourly to Daily
- **Time coverage:** Last 7-30 days
- **Data source:** ERA5, CMEMS
- **Data latency:** NRT to 5 days delay
- **Missing data handling:** `NaN`
- **Checksum algorithm:** SHA-256

### `bathymetry.nc`
- **Variable names:** `elevation`
- **Units:** Meters
- **Spatial CRS:** EPSG:3031 (Antarctic Polar Stereographic)
- **Spatial resolution:** 0.1°
- **Temporal resolution:** Static
- **Time coverage:** Static
- **Data source:** GEBCO_2026
- **Data latency:** Static
- **Missing data handling:** `NaN`
- **Checksum algorithm:** SHA-256

### `metadata.json`
- Metadata about processing pipeline, checksums, and timestamps.

## Data Source Verification

- **OSI-SAF Sea Ice:** 
  - URL: Copernicus Marine Service (SEAICE_GLO_SEAICE_L4_NRT_OBSERVATIONS_011_001)
  - License: Copernicus License
  - Attribution: E.U. Copernicus Marine Service Information
- **CMEMS Ocean Currents:**
  - URL: Copernicus Marine Service (GLOBAL_MULTIYEAR_PHY_001_030)
  - License: Copernicus License
  - Attribution: E.U. Copernicus Marine Service Information
- **ERA5 Weather:**
  - URL: Copernicus Climate Data Store (reanalysis-era5-single-levels)
  - License: Copernicus License
  - Attribution: Generated using Copernicus Climate Change Service information
- **BYU/NIC Icebergs:**
  - URL: https://www.scp.byu.edu/data/iceberg/database1.html
  - License: Public Domain / Academic Use
  - Attribution: Brigham Young University Center for Remote Sensing
- **GEBCO Bathymetry:**
  - URL: https://www.gebco.net/
  - License: Public Domain
  - Attribution: GEBCO Compilation Group
