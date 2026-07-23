class ExecutionConfidenceModel:
    def calculate(self, plan_confidence: float, step_results: list) -> float:
        fails = sum(1 for r in step_results if r.status != "SUCCESS")
        if fails > 0:
            return 0.0
        return plan_confidence
