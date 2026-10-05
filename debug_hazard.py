from backend.science.icenet_adapter import forecast_sic
from backend.science.iceberg_model import predict_iceberg_trajectory
from backend.science.route_optimizer import build_hazard_field
import numpy as np

print("=" * 60)
print("SIC FORECAST")
print("=" * 60)
sic = forecast_sic(threshold=0.7)
print(f"Keys: {list(sic.keys())}")
print(f"Mean shape: {sic['mean'].shape}")
print(f"Mean min/max/avg: {sic['mean'].min():.3f} / {sic['mean'].max():.3f} / {sic['mean'].mean():.3f}")
print(f"prob_exceeds_threshold shape: {sic.get('prob_exceeds_threshold', 'MISSING').shape if hasattr(sic.get('prob_exceeds_threshold'), 'shape') else 'MISSING'}")
if hasattr(sic.get('prob_exceeds_threshold'), 'shape'):
    p = sic['prob_exceeds_threshold']
    print(f"P(SIC>0.7) min/max/avg: {p.min():.3f} / {p.max():.3f} / {p.mean():.3f}")

print()
print("=" * 60)
print("ICEBERG TRAJECTORY")
print("=" * 60)
berg = predict_iceberg_trajectory(start_lat=-69.4, start_lon=76.2)
print(f"Keys: {list(berg.keys())}")
print(f"Ensemble size: {len(berg.get('ensemble', []))}")
if berg.get('baseline'):
    print(f"Baseline keys: {list(berg['baseline'].keys())}")
    print(f"Baseline lat last: {berg['baseline'].get('lat', [])[-1] if berg['baseline'].get('lat') else 'MISSING'}")
    print(f"Baseline lon last: {berg['baseline'].get('lon', [])[-1] if berg['baseline'].get('lon') else 'MISSING'}")

print()
print("=" * 60)
print("HAZARD FIELD")
print("=" * 60)
hazard = build_hazard_field(sic, berg)
print(f"Hazard shape: {hazard.shape}")
print(f"Hazard min/max/avg: {hazard.min():.3f} / {hazard.max():.3f} / {hazard.mean():.3f}")
print(f"Non-zero cells: {(hazard > 0).sum()}")
print(f"Cells with hazard > 0.5: {(hazard > 0.5).sum()}")
