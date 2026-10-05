$ErrorActionPreference = "Continue"
.\.venv\Scripts\Activate.ps1

Write-Host "--- VERIFY ENV ---"
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
user = os.getenv('CMEMS_USERNAME')
pwd = os.getenv('CMEMS_PASSWORD')
key = os.getenv('CDSAPI_KEY')
print(f'User: {user}')
print(f'Password length: {len(pwd) if pwd else 0} (expected 16)')
print(f'CDS key length: {len(key) if key else 0} (expected 36)')
"

Write-Host "--- TEST CMEMS API ---"
python -c "
from dotenv import load_dotenv
import os
import copernicusmarine
load_dotenv()
# Set standard variables expected by the library just in case
os.environ['COPERNICUSMARINE_USERNAME'] = os.getenv('CMEMS_USERNAME', '')
os.environ['COPERNICUSMARINE_PASSWORD'] = os.getenv('CMEMS_PASSWORD', '')
result = copernicusmarine.describe()
print('CMEMS API OK')
"
$cmems_ok = $?

if ($cmems_ok) {
    Write-Host "--- RUN DOWNLOAD ---"
    python scripts/download_data.py
} else {
    Write-Host "CMEMS API failed, skipping download."
}
