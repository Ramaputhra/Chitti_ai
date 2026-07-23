class DecisionPolicyEngine:
    def __init__(self, registry):
        self.registry = registry
        
    def evaluate(self, candidate, budget: int) -> bool:
        if budget <= 0:
            return False
        # Mock policy check: Reject any intent involving explicit CLI mechanics
        if "bash" in candidate.proposed_intent.lower() or "click" in candidate.proposed_intent.lower():
            return False
        return True
