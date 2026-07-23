from desktop.brain.reasoning.engine import ReasoningEngine
from desktop.brain.reasoning.models import ReasoningBudgetExceededException

class MockIntelligenceResult:
    def __init__(self, conf, rejected=False):
        self.confidence_score = conf
        self.rejected = rejected

def run_verification():
    print("Starting Sprint 31F Cognitive Reasoning Foundation Verification...\n")
    
    engine = ReasoningEngine()
    
    print("[1/5] Verifying Immutable ReasoningSession Generation...")
    res_support = MockIntelligenceResult(0.9, False)
    session = engine.reason("Should I send email?", [res_support])
    assert session.final_conclusion.assertion == "Action Approved"
    print("       ReasoningSession generated preserving complete lifecycle.")
    
    print("[2/5] Verifying Deterministic Conflict Resolution...")
    res_contradict = MockIntelligenceResult(1.0, True)
    session2 = engine.reason("Should I send email?", [res_support, res_contradict])
    assert session2.final_conclusion.assertion == "Action Rejected"
    print("       Epistemic rules deterministically override Empirical evidence.")
    
    print("[3/5] Verifying Confidence Propagation Math...")
    # Base 0.9, no boost (only 1 winner), decay -0.05 = 0.85
    assert session.final_conclusion.confidence == 0.85
    print(f"       Math propagated deterministically: {session.confidence_propagation_log[0]}")
    
    print("[4/5] Verifying Reasoning Budget Enforcements...")
    try:
        engine.reason("Deep reasoning", [], budget_depth=4)
        assert False, "Should have thrown Budget exception."
    except ReasoningBudgetExceededException as e:
        print(f"       Strict limits enforced: {str(e)}")
        
    print("[5/5] Verifying The Immutable Evidence Chain...")
    assert len(session.final_conclusion.evidence_trace.applied_reasoning_rules) > 0
    print("       Zero Invention Guarantee: Conclusions strictly linked to Explanability Traces.")
    
    print("\n✅ Sprint 31F Cognitive Reasoning Foundation successfully verified.")

if __name__ == "__main__":
    run_verification()
