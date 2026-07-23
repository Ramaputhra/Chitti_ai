import time
from desktop.models.interaction import InteractionEnvelope
from desktop.models.memory import MemorySnapshot
from desktop.models.cognition import PlanningDecision, HybridPlanningPolicy, PlanningRoute
from desktop.app.planner_contracts import IPlannerStrategy
from desktop.app.intent_manager import PendingIntentStore
import uuid
import datetime

class HybridPlannerStrategy(IPlannerStrategy):
    """
    An orchestrator that delegates to other planner strategies.
    Evaluates routing policy (Replay -> Deterministic -> LLM -> Clarification).
    """
    def __init__(self, 
                 deterministic_planner: IPlannerStrategy, 
                 llm_planner: IPlannerStrategy,
                 clarification_planner: IPlannerStrategy,
                 policy: HybridPlanningPolicy,
                 intent_store: PendingIntentStore,
                 replay_strategy: IPlannerStrategy = None):
        self.deterministic_planner = deterministic_planner
        self.llm_planner = llm_planner
        self.clarification_planner = clarification_planner
        self.policy = policy or HybridPlanningPolicy()
        self.intent_store = intent_store
        self.replay_strategy = replay_strategy
        
    def parse_intent(self, interaction, context):
        pass

    def formulate_decision(self, intent, context):
        pass

    def create_plan(self, decision, interaction, session_id):
        pass
        
    def _evaluate_route(self, interaction: InteractionEnvelope) -> PlanningRoute:
        # Example policy rules for routing
        
        # Policy: Refusal
        if "delete all" in interaction.payload.lower():
            return PlanningRoute.REJECT
            
        # Policy: Cost / Availability Limits
        if self.policy.is_offline or self.policy.cost_budget_exceeded or self.policy.provider_health == "UNAVAILABLE":
            return PlanningRoute.DETERMINISTIC
            
        # Policy: Complexity hints (simple regex triggers deterministic immediately)
        if interaction.payload.lower().startswith("set timer"):
            return PlanningRoute.DETERMINISTIC
            
        # Policy: Knowledge queries go to LLM immediately
        if interaction.payload.lower().startswith("explain"):
            return PlanningRoute.LLM
            
        return PlanningRoute.HYBRID
        
    async def plan(self, interaction: InteractionEnvelope, memory: MemorySnapshot) -> PlanningDecision:
        start_time = time.time()
        
        # 1. Evaluate Replay Strategy if configured (COG-31E)
        if self.replay_strategy:
            try:
                replay_decision = await self.replay_strategy.plan(interaction, memory)
                from desktop.models.cognition import DecisionQuality
                if replay_decision and replay_decision.confidence != DecisionQuality.REJECTED:
                    plan_obj = getattr(replay_decision, "plan", None)
                    if plan_obj and getattr(plan_obj, "workflows", []):
                        print(f"[HybridPlanner] 🔄 Replay Strategy Accepted Candidate. Bypassing LLM.")
                        return replay_decision
            except Exception as e:
                print(f"[HybridPlanner] ⚠️ Replay Strategy evaluation error: {e}. Falling back...")

        route = self._evaluate_route(interaction)
        
        print(f"[HybridPlanner] 🧭 Selected Route: {route.value}")
        
        decision = None
        
        if route == PlanningRoute.REJECT:
            decision = PlanningDecision(
                workflow_name="PolicyRejectionWorkflow",
                confidence=1.0,
                parameters={"reason": "Policy forbids AI interpretation"},
                requires_approval=False
            )
            
        elif route == PlanningRoute.DETERMINISTIC:
            decision = await self.deterministic_planner.plan(interaction, memory)
            
        elif route == PlanningRoute.LLM:
            decision = await self.llm_planner.plan(interaction, memory)
            if decision.workflow_name == "UnknownIntentWorkflow":
                wf_name = getattr(decision, "workflow_name", "")
                if wf_name == "UnknownIntentWorkflow":
                    # Fallback to Clarification if the LLM cannot figure it out
                    print("[HybridPlanner] ❓ LLM produced UnknownIntent. Routing to Clarification.")
                    decision = await self.clarification_planner.plan(interaction, memory)
                    route = PlanningRoute.CLARIFICATION
            
        elif route == PlanningRoute.HYBRID:
            # Try deterministic first
            decision = await self.deterministic_planner.plan(interaction, memory)
            wf_name = getattr(decision, "workflow_name", "")
            conf = getattr(decision, "confidence", None)
            conf_val = getattr(conf, "value", str(conf)) if conf else ""
            if wf_name == "FallbackWorkflow" or conf_val in ["REJECTED", "AMBIGUOUS", "UNCERTAIN"]:
                print(f"[HybridPlanner] 🔄 Deterministic failed/low confidence. Falling back to LLM.")
                decision = await self.llm_planner.plan(interaction, memory)
                wf_name_llm = getattr(decision, "workflow_name", "")
                if wf_name_llm == "UnknownIntentWorkflow":
                    print("[HybridPlanner] ❓ LLM produced UnknownIntent. Routing to Clarification.")
                    decision = await self.clarification_planner.plan(interaction, memory)
                    route = PlanningRoute.CLARIFICATION
                else:
                    route = PlanningRoute.LLM # Update telemetry route
                    
        elif route == PlanningRoute.CLARIFICATION:
            decision = await self.clarification_planner.plan(interaction, memory)
            
        # If the result is a ClarificationWorkflow, save a PendingIntent
        if decision and getattr(decision, "workflow_name", "") == "ClarificationWorkflow":
            pending = PendingIntent(
                intent="Unknown", # Or extract from current state
                missing_parameters=[decision.parameters.get("missing_parameter", "unknown")],
                captured_parameters={},
                created_at=datetime.datetime.now().isoformat(),
                expires_at=(datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat(),
                workflow_id=str(uuid.uuid4()),
                correlation_id=interaction.id,
                clarification_count=1
            )
            self.intent_store.save(pending)
            # Annotate the decision with the new workflow ID
            decision.parameters["workflow_id"] = pending.workflow_id
                
        latency = (time.time() - start_time) * 1000
        
        # Telemetry: Record planning route
        print(f"[Telemetry] 🛣️ Planning Route: {route.value} | Latency: {latency:.2f}ms")
        
        return decision
