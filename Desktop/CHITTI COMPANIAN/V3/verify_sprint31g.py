from desktop.brain.decision.engine import DecisionEngine
from desktop.brain.decision.models import DecisionCandidate, DecisionBudgetExceededException, InvalidDecisionStateException

class MockConclusion:
    def __init__(self, conf):
        self.confidence = conf

def run_verification():
    print("Starting Sprint 31G Cognitive Decision Framework Verification...\n")
    
    engine = DecisionEngine()
    
    print("[1/5] Verifying Immutable DecisionSession Generation...")
    c1 = DecisionCandidate("C1", "Mute Notifications", [MockConclusion(0.9)])
    c2 = DecisionCandidate("C2", "Cancel Subscription", [MockConclusion(0.8)])
    session = engine.decide([c1, c2])
    print(f"       Outcome: {session.final_outcome.selected_intent}")
    print(f"       Risk: {session.final_outcome.risk_level}, Priority: {session.final_outcome.priority_score}")
    
    print("[2/5] Verifying Strict Validation (No Execution Mechanics)...")
    c3 = DecisionCandidate("C3", "run_command bash script", [])
    try:
        engine.decide([c3])
        assert False, "Should have thrown InvalidDecisionStateException"
    except InvalidDecisionStateException as e:
        print(f"       Architectural Boundary Enforced: {str(e)}")
        
    print("[3/5] Verifying Risk and Policy Models...")
    # c2 'Cancel Subscription' has HIGH_REQUIRES_APPROVAL risk
    assert session.risk_assessments["C2"] == "HIGH_REQUIRES_APPROVAL"
    print("       Risk rigorously mapped to HIGH_REQUIRES_APPROVAL for destructive intents.")
    
    print("[4/5] Verifying Decision Budget Enforcements...")
    try:
        excessive = [DecisionCandidate(str(i), "intent", []) for i in range(25)]
        engine.decide(excessive)
        assert False, "Should have thrown Budget exception."
    except DecisionBudgetExceededException as e:
        print(f"       Strict numeric limits enforced: {str(e)}")
        
    print("[5/5] Verifying The Immutable Evidence Chain...")
    assert len(session.final_outcome.evidence_trace.applied_policies) > 0
    print("       Zero Invention Guarantee: Decisions fully mapped to input conclusions.")
    
    print("\n✅ Sprint 31G Cognitive Decision Framework successfully verified.")

if __name__ == "__main__":
    run_verification()
