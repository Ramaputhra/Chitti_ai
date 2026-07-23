import time
from desktop.models.reasoning import ReasoningPlan
from desktop.models.retrieval import ContextPackage
from desktop.runtimes.reasoning.policy_engine import ReasoningPolicyEngine
from desktop.runtimes.reasoning.decision_engine import DecisionEngine
from desktop.runtimes.reasoning.plan_builder import PlanBuilder
from desktop.runtimes.reasoning.reasoning_cache import ReasoningCache

class ReasoningRuntime:
    """
    The deterministic "brain" of CHITTI.
    Orchestrates: Policy Engine -> Decision Engine -> Plan Builder.
    Rule 293: Produces plan, doesn't execute.
    Rule 296: Never executes capabilities.
    Rule 297: Never retrieves directly.
    Rule 298: Never calls LLMs directly.
    """
    def __init__(self, service_registry=None, event_bus=None):
        self.policy_engine = ReasoningPolicyEngine()
        self.decision_engine = DecisionEngine(service_registry)
        self.plan_builder = PlanBuilder()
        self.cache = ReasoningCache()
        self.event_bus = event_bus

    def _emit(self, event_name: str, payload: dict):
        if self.event_bus:
            self.event_bus.publish(event_name, payload)

    def generate_plan(self, intent: str, context: ContextPackage) -> ReasoningPlan:
        """
        Takes the user intent and the active ContextPackage and produces a ReasoningPlan 
        for the Planner to orchestrate.
        """
        start_time = time.time()
        
        # 1. Cache Check
        # Optional: hash context if it heavily influences reasoning
        cached_plan = self.cache.get(intent)
        if cached_plan:
            self._emit("ReasoningCacheHit", {"intent": intent})
            return cached_plan
            
        self._emit("ReasoningStarted", {"intent": intent})

        # 2. Policy Evaluation
        policy_results = self.policy_engine.evaluate(intent)
        
        # 3. Decision Engine
        decisions, traces = self.decision_engine.evaluate(intent, policy_results, context)
        
        # 4. Plan Builder
        elapsed_ms = int((time.time() - start_time) * 1000)
        plan = self.plan_builder.build(decisions, traces, elapsed_ms)
        
        # 5. Cache and return
        self.cache.set(intent, plan)
        self._emit("ReasoningPlanGenerated", {"intent": intent, "strategy": plan.strategy.value})
        
        return plan
