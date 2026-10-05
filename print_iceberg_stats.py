import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.abspath('.'))
from backend.science.iceberg_model import predict_iceberg_trajectory

def main():
    print("Testing iceberg model execution and runtime...")
    t0 = time.time()
    res = predict_iceberg_trajectory(horizon_hours=120)
    t1 = time.time()
    
    print("\nSample Output:")
    print(f"Model used: {res['model']}")
    print(f"Ensemble size: {len(res['ensemble'])} members")
    print(f"Runtime: {t1 - t0:.3f} seconds")
    
    baseline = res['baseline']
    start_lat, start_lon = baseline['lat'][0], baseline['lon'][0]
    end_lat, end_lon = baseline['lat'][-1], baseline['lon'][-1]
    
    # Calculate physical displacement
    lat_diff = abs(end_lat - start_lat)
    lon_diff = abs(end_lon - start_lon) * np.cos(np.radians(start_lat))
    dist_km = np.sqrt(lat_diff**2 + lon_diff**2) * 111.32
    
    print(f"Baseline displacement (120h): {dist_km:.2f} km")
    print(f"Final coordinates: ({end_lat:.4f}, {end_lon:.4f})")
    
    u = res['uncertainty']
    print(f"Uncertainty Spread: P50=({u['p50']['lat']:.3f}), P90=({u['p90']['lat']:.3f})")

if __name__ == '__main__':
    main()
