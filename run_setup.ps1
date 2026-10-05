$ErrorActionPreference = "Continue"
.\.venv\Scripts\Activate.ps1
if (-not $?) { Write-Host "Failed to activate venv." }

Write-Host "--- RESUMING PIP INSTALL ---"
pip install --timeout 600 --retries 10 --no-cache-dir=false -r requirements.txt
if (-not $?) {
    Write-Host "Pip install failed, trying large packages individually..."
    pip install --timeout 600 --retries 10 rasterio
    pip install --timeout 600 --retries 10 scipy
    pip install --timeout 600 --retries 10 geopandas
    pip install --timeout 600 --retries 10 copernicusmarine
    pip install --timeout 600 --retries 10 -r requirements.txt
}

Write-Host "--- PYTHON VERSION ---"
python --version

Write-Host "--- VERIFY INSTALLATION ---"
python -c "
import xarray
import netCDF4
import numpy
import pandas
import requests
import pyproj
import rasterio
import geopandas
import shapely
import scipy
import loguru
import dotenv
import copernicusmarine
import cdsapi
print('All core packages imported successfully')
"

Write-Host "--- VERIFY CFGRIB ---"
python -c "import cfgrib; print('cfgrib OK')"

Write-Host "--- HELP TESTS ---"
python scripts/download_data.py --help
python scripts/preprocess.py --help
python scripts/verify_data.py --help

Write-Host "--- CMEMS LOGIN ---"
# Passing password via stdin
Write-Output "V7!qR2#nL9@xP4`$z" | copernicusmarine login --username mdsufiyan.04 --overwrite-configuration-file

Write-Host "--- CDS API ---"
python -c "
import cdsapi
c = cdsapi.Client()
print('CDS client initialized OK')
"
