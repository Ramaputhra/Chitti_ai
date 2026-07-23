from dataclasses import dataclass

@dataclass
class LatencyBudget:
    observe_ms: int = 100
    context_ms: int = 150
    memory_write_ms: int = 20
    prediction_ms: int = 300
    planner_ms: int = 500
    workflow_dispatch_ms: int = 20

class LatencyMonitor:
    """Enforces hard limits on runtime pipeline latency."""
    def __init__(self, budget: LatencyBudget = LatencyBudget()):
        self.budget = budget
        
    def check_compliance(self, stage: str, actual_ms: float) -> bool:
        budget_limit = getattr(self.budget, f"{stage.lower()}_ms", None)
        if budget_limit is None:
            return True # Unbudgeted stage
            
        if actual_ms > budget_limit:
            print(f"[LATENCY ALERT] {stage} took {actual_ms}ms (Budget: {budget_limit}ms)")
            return False
            
        return True
