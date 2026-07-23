import asyncio
from desktop.integration.cognitive_trace import CognitiveTraceLogger, TraceNode
from desktop.integration.latency import LatencyMonitor
from desktop.integration.chaos import ChaosMonkey, FAULTS
from datetime import datetime
import time

async def simulate_morning_resume(chaos: ChaosMonkey, monitor: LatencyMonitor, logger: CognitiveTraceLogger):
    trace_id = "trc-morning-resume-101"
    logger.start_trace(trace_id, "User Boot")
    print("\n--- Running Scenario: Morning Resume ---")
    
    # Observe
    start = time.time()
    if chaos.check_fault(FAULTS["WORLD_RUNTIME_UNAVAILABLE"]):
        print(" -> Graceful Degradation: World Runtime offline. Using stale context.")
    else:
        # Mock Observe
        await asyncio.sleep(0.05) 
    monitor.check_compliance("Observe", (time.time() - start) * 1000)
    
    # Predict / Continuity
    start = time.time()
    if chaos.check_fault(FAULTS["GPU_OOM"]):
        print(" -> Graceful Degradation: GPU OOM. Falling back to CPU model for prediction.")
        await asyncio.sleep(0.25)
    else:
        await asyncio.sleep(0.15)
    monitor.check_compliance("Prediction", (time.time() - start) * 1000)
    
    # Planner
    start = time.time()
    await asyncio.sleep(0.40)
    monitor.check_compliance("Planner", (time.time() - start) * 1000)
    
    print("Scenario Output: PASSIVE Toast - 'Resume Sprint 60?'")
    logger.complete_trace(trace_id)


async def execute_integration_suite():
    chaos = ChaosMonkey()
    monitor = LatencyMonitor()
    logger = CognitiveTraceLogger()
    
    # 1. Clean Run
    await simulate_morning_resume(chaos, monitor, logger)
    
    # 2. Chaos Run: UIA Fails
    chaos.inject_fault(FAULTS["WORLD_RUNTIME_UNAVAILABLE"])
    await simulate_morning_resume(chaos, monitor, logger)
    chaos.clear_faults()
    
    # 3. Chaos Run: GPU OOM
    chaos.inject_fault(FAULTS["GPU_OOM"])
    await simulate_morning_resume(chaos, monitor, logger)
    
if __name__ == "__main__":
    asyncio.run(execute_integration_suite())
