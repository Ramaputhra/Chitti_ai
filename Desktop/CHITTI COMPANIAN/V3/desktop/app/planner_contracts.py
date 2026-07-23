from abc import ABC, abstractmethod
from typing import Optional
from desktop.models.interaction import InteractionEnvelope
from desktop.models.memory import MemorySnapshot
from desktop.models.cognition import PlanningDecision, ExecutionPlan, Intent

class IPlannerStrategy(ABC):
    """
    Defines the contract for how interactions are transformed into ExecutionPlans.
    Allows swapping Deterministic strategies for LLM or Hybrid strategies
    without modifying the PlannerRuntime.
    """
    
    @abstractmethod
    def parse_intent(self, interaction: InteractionEnvelope, context: MemorySnapshot) -> Intent:
        """Step 1: Determine what the user wants."""
        pass

    @abstractmethod
    def formulate_decision(self, intent: Intent, context: MemorySnapshot) -> PlanningDecision:
        """Step 2: Decide what to do about it."""
        pass

    @abstractmethod
    def create_plan(self, decision: PlanningDecision, interaction: InteractionEnvelope, session_id: str) -> ExecutionPlan:
        """Step 3: Formalize the decision into an immutable manifest."""
        pass
