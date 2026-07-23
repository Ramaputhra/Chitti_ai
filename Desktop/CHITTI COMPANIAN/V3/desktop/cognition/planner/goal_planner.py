from desktop.models.cognition import ReasoningContext, Goal
from desktop.cognition.planner.backend import PlannerBackend, DeterministicBackend

class GoalPlanner:
    """
    Rule 55: Planner Authority.
    The primary semantic reasoning interface. It is the sole component 
    authorized to establish an active goal or user intent based on the ReasoningContext.
    """
    def __init__(self, backend: PlannerBackend = None):
        self.backend = backend or DeterministicBackend()
        
    def select_goal(self, context: ReasoningContext) -> Goal:
        # Pass the context directly to the configured backend
        return self.backend.select_goal(context)
