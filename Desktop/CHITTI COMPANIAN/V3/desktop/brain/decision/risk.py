class RiskEvaluationEngine:
    def evaluate(self, candidate, budget: int) -> str:
        if budget <= 0:
            return "UNKNOWN"
        intent = candidate.proposed_intent.lower()
        if "delete" in intent or "cancel" in intent:
            return "HIGH_REQUIRES_APPROVAL"
        if "modify" in intent:
            return "MEDIUM"
        return "LOW"
