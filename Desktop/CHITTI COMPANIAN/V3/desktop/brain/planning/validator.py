from desktop.brain.planning.models import InvalidPlanningStateException

class PlanValidator:
    def validate_plan(self, plan, original_intent: str, budget: int) -> bool:
        if budget <= 0:
            return False
            
        for s in plan.steps:
            if s.payload.get("invented_intent"):
                raise InvalidPlanningStateException("PlanCompiler illegally invented new goals")
                
        return True
