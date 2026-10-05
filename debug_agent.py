import asyncio
from backend.agents.graph import run_agent

async def main():
    result = await run_agent("Is it safe to sail from Bharati to Maitri?")
    
    print("=" * 60)
    print("AGENT STATE")
    print("=" * 60)
    print(f"Intent: {result.get('intent')}")
    print(f"Confidence: {result.get('intent_confidence')}")
    print(f"Validation passed: {result.get('validation_passed')}")
    print(f"Routes count: {len(result.get('routes', []))}")
    print(f"Route labels: {[r['label'] for r in result.get('routes', [])]}")
    print(f"Pareto count: {len(result.get('pareto_routes', []))}")
    print(f"Pareto labels: {[r['label'] for r in result.get('pareto_routes', [])]}")
    print(f"Selected route: {result.get('selected_route', {}).get('label') if result.get('selected_route') else None}")
    print(f"Abstained: {result.get('abstained')}")
    print(f"Evidence why_selected count: {len(result.get('evidence', {}).get('why_selected', []))}")
    print()
    print("Trace:")
    for step in result.get('trace', []):
        print(f"  {step['step']:2d}. {step['node']:30s} {step['duration_ms']:8.1f}ms")

asyncio.run(main())
