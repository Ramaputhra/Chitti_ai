class PrerequisiteValidator:
    def validate(self, steps: list, budget: int) -> list:
        if budget <= 0:
            return []
        
        logs = []
        for s in steps:
            if s.action_type == "REQUIRES_ADMIN":
                logs.append(f"{s.step_id}: FAILED (No Admin)")
                return logs
            logs.append(f"{s.step_id}: PASSED")
        return logs
