import requests
import json
import time

print("=" * 60)
print("TEST 1: Health endpoint")
print("=" * 60)

try:
    r = requests.get("http://localhost:8000/health", timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
except Exception as e:
    print(f"FAILED: {e}")
    exit(1)

print()
print("=" * 60)
print("TEST 2: /analyze endpoint (this takes ~20s)")
print("=" * 60)

payload = {"query": "Is it safe to sail from Bharati to Maitri?"}

try:
    start = time.time()
    r = requests.post(
        "http://localhost:8000/analyze",
        json=payload,
        timeout=120
    )
    elapsed = time.time() - start
    
    print(f"Status: {r.status_code}")
    print(f"Time: {elapsed:.1f}s")
    
    if r.status_code == 200:
        data = r.json()
        print()
        print("=== KEY FIELDS ===")
        print(f"run_id: {data.get('run_id')}")
        print(f"intent: {data.get('intent', {}).get('intent')}")
        print(f"confidence: {data.get('intent', {}).get('confidence')}")
        print(f"routes count: {len(data.get('routes', []))}")
        print(f"selected_route: {data.get('selected_route', {}).get('label')}")
        print(f"abstained: {data.get('abstained')}")
        print(f"evidence keys: {list(data.get('evidence', {}).keys())}")
        print(f"trace steps: {len(data.get('trace', []))}")
        print(f"total duration: {data.get('total_duration_seconds'):.1f}s")
        
        # Save full response for inspection
        with open("test_response.json", "w") as f:
            json.dump(data, f, indent=2)
        print()
        print("Full response saved to test_response.json")
    else:
        print(f"ERROR: {r.text}")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
