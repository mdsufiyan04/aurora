import time
import asyncio
from backend.agents.graph import run_agent

async def main():
    start = time.time()
    result = await run_agent("Is it safe to sail from Bharati to Maitri?")
    total = time.time() - start
    
    print(f"\nTotal: {total:.1f}s")
    print("\nPer-node timing:")
    for step in result["trace"]:
        print(f"  {step['node']:30s} {step['duration_ms']:8.0f}ms")

if __name__ == "__main__":
    asyncio.run(main())
