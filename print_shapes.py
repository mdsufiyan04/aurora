import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from backend.science.icenet_adapter import forecast_sic

def main():
    print('\nSample forecast_sic() shapes:')
    s = forecast_sic()
    for k, v in s.items():
        if hasattr(v, 'shape'):
            print(f'{k}: {v.shape}')
        elif isinstance(v, dict):
            print(f'{k}: {{' + ', '.join([f"'{sub_k}': {sub_v.shape if hasattr(sub_v, 'shape') else type(sub_v)}" for sub_k, sub_v in v.items()]) + '}')
        else:
            print(f'{k}: {type(v).__name__} = {v}')

if __name__ == '__main__':
    main()
