from desktop.brain.decision.models import InvalidDecisionStateException

class DecisionValidator:
    def validate_outcome(self, outcome, budget: int) -> bool:
        if budget <= 0:
            return False
        # Reject if intent looks like execution ("How" instead of "What")
        intent = outcome.selected_intent.lower()
        forbidden_mechanics = ["run_command", "api_call", "playwright"]
        for mech in forbidden_mechanics:
            if mech in intent:
                raise InvalidDecisionStateException(f"Intent leaked execution mechanics: {mech}")
        return True
