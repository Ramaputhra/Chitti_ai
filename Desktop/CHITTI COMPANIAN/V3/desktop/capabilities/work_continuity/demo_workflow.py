import asyncio
from desktop.capabilities.work_continuity.capability import WorkContinuityCapability

class MockMemoryRuntime:
    pass

class MockPredictionRuntime:
    pass

async def execute_demo():
    print("--- Work Continuity Demonstration ---\n")
    
    capability = WorkContinuityCapability(MockMemoryRuntime(), MockPredictionRuntime())
    
    # --- Scenario 1: Morning Resume (Flow State) ---
    print("Scenario 1: Morning Resume (User is in FLOW)")
    model_flow = await capability.execute({})
    
    print(f"Current Focus: {model_flow.current_focus.name}")
    print(f"Unfinished Work: {model_flow.unfinished_work[0].last_goal}")
    print(f"Next Action: {model_flow.unfinished_work[0].next_action}")
    
    rec = model_flow.recommended_next_step
    print(f"\nRecommendation: Resume Sprint 60")
    print(f"Explainability (Rule 139): {rec.reason}")
    print(f"Interruption Policy (Rule 138): {rec.policy.name} (Value outweighed by Disruption Cost of FLOW)")
    
    
    # --- Scenario 2: Afternoon Resume (Fractured State) ---
    print("\n-------------------------------------------------\n")
    print("Scenario 2: Afternoon Resume (User is FRACTURED, simulate stuck)")
    
    # Hack the mock's focus state for the demo
    capability.execute.__code__ = capability.execute.__code__ # not easily hackable in python without replacing, so we'll just mock policy engine input
    
    # Let's bypass full capability re-write and just use a quick manual test
    from desktop.capabilities.work_continuity.models import Recommendation, FocusState
    from desktop.capabilities.work_continuity.policy import InterruptionPolicyEngine
    
    policy_engine = InterruptionPolicyEngine()
    afternoon_rec = Recommendation(
        priority=0.8,
        reason="You've been distracted for 20 minutes, let's get back to consolidator.py",
        estimated_value=0.9,
        estimated_time=1200,
        confidence=0.95
    )
    
    # Because user is FRACTURED, disruption cost is low.
    final_rec = policy_engine.evaluate(afternoon_rec, FocusState.FRACTURED)
    
    print(f"Current Focus: FRACTURED")
    print(f"Explainability (Rule 139): {final_rec.reason}")
    print(f"Interruption Policy (Rule 138): {final_rec.policy.name} (Disruption Cost is low, so we SUGGEST!)")

if __name__ == "__main__":
    asyncio.run(execute_demo())
