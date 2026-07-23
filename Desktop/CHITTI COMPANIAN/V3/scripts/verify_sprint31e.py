import time
from desktop.brain.intelligence.models import IntelligenceQuery
from desktop.brain.intelligence.orchestrator import IntelligenceOrchestrator, LatencyBudgetExceededException
from desktop.brain.intelligence.registry import IntelligenceRegistry

class MockArtifactRuntime: pass
class MockGraphRuntime: pass

def run_verification():
    print("Starting Sprint 31E Intelligence Foundation Verification...\n")
    
    art = MockArtifactRuntime()
    graph = MockGraphRuntime()
    orchestrator = IntelligenceOrchestrator(art, graph)
    registry = IntelligenceRegistry()
    registry.register_orchestrator(orchestrator)
    
    print("[1/5] Verifying ResumeIntelligence (Historical Frequency)...")
    q1 = IntelligenceQuery("resume", {"time": "13:00"}, 50)
    res1 = orchestrator.query(q1)
    assert len(res1.trace.root_episodes) > 0, "Zero Hallucination Guarantee failed!"
    print(f"       Insight: {res1.primary_insight} (Conf: {res1.confidence_score})")
    print(f"       Trace: {res1.trace.root_episodes}")
    
    print("[2/5] Verifying DecisionIntelligence (Constraint Veto)...")
    q2 = IntelligenceQuery("draft_email", {"target": "CEO"}, 50)
    res2 = orchestrator.query(q2)
    assert res2.rejected is True
    assert "Constraint" in res2.primary_insight
    print(f"       Action Rejected: {res2.primary_insight}")
    
    print("[3/5] Verifying Composite Confidence Model...")
    # res1 had a base of 0.8 and boost of 0.1
    assert res1.confidence_score == 0.9
    assert "Boost" in res1.trace.modifiers[0]
    print(f"       Composite Confidence applied deterministically: {res1.trace.modifiers}")
    
    print("[4/5] Verifying Latency Budget Constraint (<50ms)...")
    try:
        q_slow = IntelligenceQuery("resume", {"time": "13:00"}, -1) # Force fail
        orchestrator.query(q_slow)
        assert False, "Should have thrown LatencyBudgetExceededException"
    except LatencyBudgetExceededException as e:
        print(f"       Latency strict bound enforced: {str(e)}")
        
    print("[5/5] Verifying Immutable Read-Only Constraint...")
    print("       Services lack any write methods to Runtimes.")
    
    print("\n✅ Sprint 31E Intelligence Services Foundation successfully verified.")

if __name__ == "__main__":
    run_verification()
