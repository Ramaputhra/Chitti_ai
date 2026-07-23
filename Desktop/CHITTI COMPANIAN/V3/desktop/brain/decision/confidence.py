class DecisionConfidenceModel:
    def calculate(self, priority: int, risk: str) -> float:
        base = min(1.0, priority / 100.0)
        if risk == "HIGH_REQUIRES_APPROVAL":
            base = min(base, 0.5)
        return base
