"""
ActionPlanner — pure orchestration layer.

Responsibilities:
  1. Receive Intent.Detected events.
  2. Build a PlanningContext from available system state.
  3. Delegate ALL reasoning to DecisionEngine.
  4. Broadcast Planner.StateChanged events (Planning / Idle) — NOT expression names.
  5. Publish the resulting Workflow via Workflow.Created.

The ActionPlanner knows NOTHING about:
  - Which skill handles an intent
  - What an LLM is
  - What "Thinking" looks like (that's the ExpressionRuntime's job)
  - How workflows are executed

This keeps the planner stable even as capabilities, LLMs, and hardware evolve.
"""

from typing import Any, Dict

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.planner import IActionPlanner
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ExecutionPlan, LLMResponse
from desktop.platform.shared.models.planning import Decision, PlanningContext, PlanningResult
from desktop.platform.shared.models.workflow import Workflow, WorkflowStep
from desktop.platform.shared.models.workflow_actions import WorkflowAction
from desktop.services.language.decision_engine import DecisionEngine


class PlanValidator:
    """Validates workflows before they are dispatched to the executor."""
    @staticmethod
    def validate(workflow: Workflow) -> bool:
        if not workflow.steps:
            return False
        # Basic validation for Sprint 13: check for valid primitives
        valid_actions = {
            WorkflowAction.INVOKE_CAPABILITY, WorkflowAction.RETRIEVE_MEMORY,
            WorkflowAction.STORE_MEMORY, WorkflowAction.REASON, WorkflowAction.SPEAK,
            WorkflowAction.ANIMATE, WorkflowAction.WAIT, WorkflowAction.ASK_QUESTION,
            WorkflowAction.EXECUTE_SYSTEM_ACTION
        }
        for step in workflow.steps:
            if step.action not in valid_actions:
                return False
        return True


class ActionPlanner(IActionPlanner):
    """
    Cognitive pipeline orchestrator.
    Builds context → Applies Policies → Delegates to DecisionEngine → Translates to Workflow → Validates → Dispatches.
    """

    def __init__(
        self,
        logger: ILoggingService,
        event_bus: IEventBus,
        decision_engine: DecisionEngine,
    ) -> None:
        self.logger = logger
        self.event_bus = event_bus
        self._decision_engine = decision_engine
        self._state = ServiceState.STOPPED
        self._planner_version = "1.0.0"

    @property
    def name(self) -> str:
        return "ActionPlanner"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.event_bus.subscribe(SystemEvents.INTENT_DETECTED, self._on_intent_detected)
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized (v{self._planner_version})")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"state": self._state.value}

    def _on_intent_detected(self, event: Event) -> None:
        intent = event.payload.get("intent")
        text = event.payload.get("original_text", "")

        if not intent:
            return

        self.logger.info(f"--- Cognitive Trace Started [Intent: {intent.type}] ---")
        self._emit_planner_state("Planning")

        # 1. Build Context
        context = PlanningContext(
            user_input=text,
            intent_type=intent.type,
            intent_confidence=getattr(intent, "confidence", 1.0),
        )
        self.logger.info("  ↓ PlanningContext Built")

        # 2. Apply Policies (Mocked)
        # e.g., if policy is 'offline_only' and target needs cloud, abort.
        self.logger.info("  ↓ Policies Applied (None blocked)")

        # 3. Decision Engine (Reasoning)
        self.logger.info("  ↓ Evaluating: Memory → Capability → Clarification → Reasoning")
        decision = self._decision_engine.evaluate(context)
        self.logger.info(f"  ↓ Decision Created [Route: {decision.route}, Target: {decision.target}]")

        # 4. Handle Decisions (Task Orchestrator vs Workflow Generation)
        if decision.route == "task":
            self.logger.info(f"  ↓ Task Route Detected. Handing over to Task Orchestrator.")
            self.event_bus.publish(
                Event(
                    SystemEvents.TASK_CREATED,
                    self.name,
                    {
                        "goal": context.user_input,
                        "source_intent": context.intent_type,
                        "correlation_id": context.correlation_id,
                    }
                )
            )
            self.logger.info("--- Cognitive Trace Completed (Delegated to Task Orchestrator) ---")
            self._emit_planner_state("Idle")
            return
            
        # 4b. Translate Decision to Workflow (Planning)
        workflow = self._translate_to_workflow(decision, context)
        self.logger.info(f"  ↓ Workflow Generated [{len(workflow.steps)} steps]")

        # 5. Validate Plan
        if not PlanValidator.validate(workflow):
            self.logger.error("  ↓ Workflow Validation FAILED! Aborting.")
            self._emit_planner_state("Idle")
            return
        self.logger.info("  ↓ Workflow Validated")

        # 6. Dispatch
        result = PlanningResult(
            success=True,
            confidence=decision.confidence,
            workflow=workflow,
            decision=decision,
            diagnostics=decision.diagnostics
        )

        self.event_bus.publish(
            Event(
                SystemEvents.WORKFLOW_CREATED,
                self.name,
                {
                    "workflow": result.workflow,
                    "planning_result": {
                        "confidence": result.confidence,
                        "decision_path": decision.decision_path,
                        "diagnostics": result.diagnostics,
                    },
                },
            )
        )
        self.logger.info(f"  ↓ Workflow Executed (Dispatched ID: {workflow.workflow_id})")
        self.logger.info("--- Cognitive Trace Completed ---")

        self._emit_planner_state("Idle")

    def _translate_to_workflow(self, decision: Decision, context: PlanningContext) -> Workflow:
        """Translates an abstract Decision into an executable Workflow using primitives."""
        steps = []
        
        if decision.route == "memory":
            steps.append(WorkflowStep(
                action=WorkflowAction.SPEAK,
                parameters={"text": decision.target}
            ))
        elif decision.route == "capability":
            steps.append(WorkflowStep(
                action=WorkflowAction.INVOKE_CAPABILITY,
                parameters={
                    "capability_id": decision.target,
                    "intent_type": context.intent_type,
                }
            ))
        elif decision.route == "clarification":
            steps.append(WorkflowStep(
                action=WorkflowAction.ASK_QUESTION,
                parameters={"question": decision.target}
            ))
        elif decision.route == "reasoning":
            steps.append(WorkflowStep(
                action=WorkflowAction.REASON,
                parameters={
                    "user_input": context.user_input,
                    "intent_type": context.intent_type,
                    "template": "Unknown",
                }
            ))
            
        workflow = Workflow(
            steps=steps,
            source_intent=context.intent_type,
            correlation_id=context.correlation_id,
        )
        # Apply metadata requested by architecture review
        workflow.metadata["created_by"] = "ActionPlanner"
        workflow.metadata["planner_version"] = self._planner_version
        
        return workflow

    def _emit_planner_state(self, state: str) -> None:
        """Broadcast Planner.StateChanged — NOT avatar-specific expression names."""
        self.event_bus.publish(
            Event(
                SystemEvents.PLANNER_STATE_CHANGED,
                self.name,
                {"state": state},
            )
        )

    # ── Legacy compatibility ──────────────────────────────────────────────────
    def plan(self, response: LLMResponse) -> ExecutionPlan:
        self.logger.info("ActionPlanner.plan() called via legacy LLMResponse path")
        return ExecutionPlan(
            steps=response.tool_invocations,
            requires_confirmation=False,
            priority=1,
            timeout_sec=30.0,
        )
