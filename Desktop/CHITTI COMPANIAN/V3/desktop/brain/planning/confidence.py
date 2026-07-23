class PlanConfidenceModel:
    def calculate(self, base_confidence: float, prereq_logs: list) -> float:
        for log in prereq_logs:
            if "FAILED" in log:
                return 0.0
        return base_confidence
