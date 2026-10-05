import sys
import os
import time

sys.path.insert(0, os.path.abspath('.'))
from backend.science.route_optimizer import optimize_multiple_routes, pareto_filter

def main():
    print("Running Route Optimizer for Bharati -> Maitri...")
    
    t0 = time.time()
    routes = optimize_multiple_routes(-69.0, 76.0, -69.5, 12.0)
    t1 = time.time()
    
    print(f"\nOptimization completed in {t1 - t0:.3f} seconds.")
    print(f"Generated {len(routes)} unique routes (deduplicated).")
    
    print("\n--- All Routes ---")
    for i, r in enumerate(routes):
        print(f"[{r['label']}] Distance: {r['distance_km']:.1f} km | Risk: {r['expected_risk']:.3f} | MaxSIC: {r.get('max_sic_encountered', 0.0):.2f}")
        
    pareto = pareto_filter(routes)
    
    print("\n--- Pareto-Optimal Routes ---")
    for r in pareto:
        print(f"[{r['label']}] Distance: {r['distance_km']:.1f} km | Risk: {r['expected_risk']:.3f} | MaxSIC: {r.get('max_sic_encountered', 0.0):.2f}")

if __name__ == '__main__':
    main()
