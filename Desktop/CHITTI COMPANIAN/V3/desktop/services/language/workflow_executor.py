"""
[DEPRECATED] WorkflowExecutor — the execution backbone of the cognitive pipeline.
This module has been replaced by the dedicated Workflow Runtime located at `desktop/runtimes/workflow/`.
This file is kept temporarily for backward compatibility during the Sprint 18 migration.

Receives an immutable Workflow from the ActionPlanner (via Workflow.Created)
and executes each step using universal WorkflowAction primitives.

Step dispatch matrix:
  InvokeCapability   → CapabilityResolver → Skill.execute()
  Reason             → GenerateResponse (template-based fallback until LLM is live)
  Speak              → WorkflowStep.GenerateResponse with explicit text
  AskQuestion        → WorkflowStep.GenerateResponse with question text
  StoreMemory        → (mocked Sprint 13)
  RetrieveMemory     → (mocked Sprint 13)
  Animate            → Planner.StateChanged  (ExpressionRuntime picks this up)
  Wait               → time.sleep

The executor emits Planner.StateChanged("Working") on start and ("Idle") on finish,
so the ExpressionRuntime always knows when execution is active.
"""

import time
from typing import Any, Dict

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.executor import IWorkflowExecutor
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.workflow import Workflow
from desktop.platform.shared.models.workflow_actions import WorkflowAction
from desktop.services.language.capability_resolver import CapabilityResolver


class WorkflowExecutor(IWorkflowExecutor):
    def __init__(
        self,
        event_bus: IEventBus,
        logger: ILoggingService,
        capability_resolver: CapabilityResolver,
    ) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self._resolver = capability_resolver
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "WorkflowExecutor"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.event_bus.subscribe(SystemEvents.WORKFLOW_CREATED, self._on_workflow_created)
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"state": self._state.value}

    def _on_workflow_created(self, event: Event) -> None:
        workflow: Workflow = event.payload.get("workflow")
        if not workflow:
            return

        self.logger.info(
            f"WorkflowExecutor: starting workflow {workflow.workflow_id} "
            f"[intent={workflow.source_intent}, steps={len(workflow.steps)}]"
        )

        # Signal ExpressionRuntime that work is beginning
        self._emit_planner_state("Working")

        self.event_bus.publish(
            Event(SystemEvents.WORKFLOW_STARTED, self.name, {"workflow_id": workflow.workflow_id})
        )

        for step in workflow.steps:
            self.logger.info(
                f"WorkflowExecutor: executing step '{step.action}' "
                f"[workflow={workflow.workflow_id}]"
            )
            try:
                self._execute_step(step, workflow)
            except Exception as e:
                self.logger.exception(e, module=self.name)
                # Graceful degradation: continue to next step rather than halt

            self.event_bus.publish(
                Event(
                    SystemEvents.WORKFLOW_STEP_COMPLETED,
                    self.name,
                    {"workflow_id": workflow.workflow_id, "step_action": step.action},
                )
            )

        self.event_bus.publish(
            Event(
                SystemEvents.WORKFLOW_COMPLETED,
                self.name,
                {"workflow_id": workflow.workflow_id},
            )
        )

        self.logger.info(f"WorkflowExecutor: workflow {workflow.workflow_id} completed")
        self._emit_planner_state("Idle")

    def _execute_step(self, step: Any, workflow: Workflow) -> None:
        action = step.action
        params = step.parameters

        # ── InvokeCapability ──────────────────────────────────────────────────
        if action == WorkflowAction.INVOKE_CAPABILITY:
            # The DecisionEngine may embed the skill directly for efficiency,
            # or we re-resolve by capability_id for safety.
            skill = params.get("skill")
            if skill is None:
                cap_id = params.get("capability_id", "")
                resolve = self._resolver.resolve(params.get("intent_type", cap_id))
                skill = resolve.skill if resolve.can_handle else None

            if skill:
                from desktop.platform.shared.models.intent import Intent
                intent = Intent(
                    type=params.get("intent_type", "Unknown"),
                    confidence=1.0,
                )
                self.logger.info(f"WorkflowExecutor: invoking capability '{skill.name()}'")
                skill.execute(intent)
            else:
                self.logger.warning(
                    f"WorkflowExecutor: no capability found for "
                    f"'{params.get('capability_id', 'unknown')}' — falling back to Reason"
                )
                self._execute_reason_step(params, workflow)

        # ── Reason (LLM fallback / template-based) ────────────────────────────
        elif action == WorkflowAction.REASON:
            self._execute_reason_step(params, workflow)

        # ── Speak ─────────────────────────────────────────────────────────────
        elif action == WorkflowAction.SPEAK:
            text = params.get("text", "")
            self.event_bus.publish(
                Event(
                    "WorkflowStep.GenerateResponse",
                    self.name,
                    {"parameters": {"template": "Direct", "text": text}},
                )
            )

        # ── AskQuestion ───────────────────────────────────────────────────────
        elif action == WorkflowAction.ASK_QUESTION:
            question = params.get("question", "Could you clarify that?")
            self.event_bus.publish(
                Event(
                    "WorkflowStep.GenerateResponse",
                    self.name,
                    {"parameters": {"template": "AskQuestion", "text": question}},
                )
            )

        # ── StoreMemory (mocked) ──────────────────────────────────────────────
        elif action == WorkflowAction.STORE_MEMORY:
            self.logger.info(
                f"WorkflowExecutor: [MOCKED] StoreMemory — {params.get('content', '')}"
            )

        # ── RetrieveMemory (mocked) ───────────────────────────────────────────
        elif action == WorkflowAction.RETRIEVE_MEMORY:
            self.logger.info(
                f"WorkflowExecutor: [MOCKED] RetrieveMemory — {params.get('query', '')}"
            )

        # ── Animate ───────────────────────────────────────────────────────────
        elif action == WorkflowAction.ANIMATE:
            expression = params.get("expression", "Idle")
            self._emit_planner_state(expression)

        # ── Wait ──────────────────────────────────────────────────────────────
        elif action == WorkflowAction.WAIT:
            duration_ms = params.get("duration_ms", 0)
            if duration_ms > 0:
                time.sleep(duration_ms / 1000.0)

        # ── ExecuteSystemAction ───────────────────────────────────────────────
        elif action == WorkflowAction.EXECUTE_SYSTEM_ACTION:
            self.logger.info(
                f"WorkflowExecutor: [MOCKED] ExecuteSystemAction — {params.get('action', '')}"
            )

        else:
            self.logger.warning(
                f"WorkflowExecutor: unknown step action '{action}' — skipping"
            )

    def _execute_reason_step(self, params: Dict[str, Any], workflow: Workflow) -> None:
        """
        LLM reasoning fallback. Sprint 13: uses template-based response.
        Sprint 16: routes to LLMRouter via InferenceScheduler.
        """
        template = params.get("template", "Unknown")
        self.event_bus.publish(
            Event(
                "WorkflowStep.GenerateResponse",
                self.name,
                {"parameters": {"template": template}},
            )
        )

    def _emit_planner_state(self, state: str) -> None:
        self.event_bus.publish(
            Event(
                SystemEvents.PLANNER_STATE_CHANGED,
                self.name,
                {"state": state},
            )
        )
