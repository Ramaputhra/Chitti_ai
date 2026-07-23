class PriorityEvaluationEngine:
    def evaluate(self, candidate, budget: int) -> int:
        if budget <= 0:
            return 0
        base_score = 50
        if candidate.supporting_conclusions:
            conf = getattr(candidate.supporting_conclusions[0], "confidence", 0.0)
            base_score += int(conf * 10)
        return base_score
