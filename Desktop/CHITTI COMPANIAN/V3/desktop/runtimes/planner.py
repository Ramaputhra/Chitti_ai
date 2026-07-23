from datetime import datetime
from desktop.models.lifecycle import IRuntime, HealthState
from desktop.models.interaction import InteractionEnvelope, IntentResolved
from desktop.models.events import PlanCreated
from desktop.app.context import KernelContext
from desktop.app.memory_contracts import IMemoryService
from desktop.app.planner_contracts import IPlannerStrategy

class PlannerRuntime(IRuntime):
    """
    Transforms interactions and memory into immutable execution plans.
    Adheres to Rule 176 (never executes).
    """
    def __init__(self, strategy: IPlannerStrategy):
        self.strategy = strategy
        self.context = None

    @property
    def dependencies(self): 
        # Planner requires MemoryService to build snapshots
        return [IMemoryService]

    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        if hasattr(self.context, "event_bus"):
            self.context.event_bus.subscribe(IntentResolved, self.process_intent)
        return True

    async def start(self) -> bool:
        print(f"    [PlannerRuntime] Started using strategy: {getattr(self.strategy, 'version', 'unknown')}")
        return True

    async def stop(self) -> bool:
        print("    [PlannerRuntime] Stopped.")
        return True

    def health(self) -> HealthState:
        return HealthState.HEALTHY

    async def shutdown(self) -> bool:
        return True

    async def process_intent(self, event: IntentResolved):
        """
        The main entry point for the Cognitive Engine.
        Called by the Kernel when an IntentResolved event arrives.
        """
        memory_service: IMemoryService = self.context.registry.resolve(IMemoryService)
        
        # Hardcoding session_id for demonstration purposes (Sprint 79)
        session_id = "default_session"

        # 1. Store the incoming User interaction as a factual record (Rule 175)
        # In real V2, ConversationRuntime would store this before generating the intent.
        # For this sprint, we just pull it from the IntentResult for continuity.
        if hasattr(event.result, "interaction_id"):
            pass # Already recorded by Conversation or Transport if needed

        # 2. Context Assembly
        snapshot = memory_service.snapshot(session_id, workflow_id="global")

        # 3. Intent Recognition (Now just mapping structured IntentResult)
        intent = self.strategy.parse_intent(event, snapshot)

        # 4. Cognitive Decision
        decision = self.strategy.formulate_decision(intent, snapshot)

        # 5. Plan Formulation (Immutable Manifest)
        plan = self.strategy.create_plan(decision, event, session_id)

        # 6. Handoff to Execution (via EventBus)
        self.context.event_bus.publish(PlanCreated(
            timestamp=datetime.now(),
            source="PlannerRuntime",
            correlation_id=event.correlation_id,
            domain="Cognition",
            action="PlanCreated",
            payload={
                "interaction_id": getattr(plan, 'interaction_id', ''),
                "plan_id": getattr(plan, 'plan_id', ''),
                "session_id": getattr(plan, 'session_id', ''),
                "planner_version": getattr(plan, 'planner_version', '1.0.0')
            }
        ))
        
        # We also publish the raw ExecutionPlan for the upcoming ExecutionRuntime to subscribe to
        self.context.event_bus.publish(plan)
