import logging
import time
from typing import Any, Dict

from desktop.platform.ai.capability_resolver import CapabilityResolver
from desktop.platform.ai.planner_runtime import PlannerRuntime
from desktop.models.planner_models import (
    CapabilityResolvedEvent, ExecutionPlanCreatedEvent, 
    PlanFailedEvent, PlanFailureReason
)

logger = logging.getLogger(__name__)

class RuntimeKernel:
    """
    The heart of CHITTI.
    Orchestrates the lifecycle between Semantic Intents, Planning, and Execution.
    """
    def __init__(self, event_bus: Any, resolver: CapabilityResolver, planner: PlannerRuntime):
        self.event_bus = event_bus
        self.resolver = resolver
        self.planner = planner
        
        # Subscribe to output of Semantic Runtime
        self.event_bus.subscribe("INTENT_GENERATED", self.handle_intent)
        
        # Subscribe to execution lifecycle
        self.event_bus.subscribe("CAPABILITY_COMPLETED", self.handle_capability_completed)
        self.event_bus.subscribe("VERIFICATION_COMPLETED", self.handle_verification_completed)

    def handle_intent(self, event: Dict[str, Any]) -> None:
        payload = event.get("payload", {})
        intent = payload.get("event").desktop_intent
        
        if not intent:
            return

        logger.info(f"Runtime Kernel received Intent: {intent.action.name}")
        
        # 1. Capability Resolution
        manifest = self.resolver.resolve(intent)
        
        if not manifest:
            logger.error("Kernel Failed: UNKNOWN_CAPABILITY")
            failure = PlanFailedEvent(
                intent_id=intent.session_id,
                reason=PlanFailureReason.UNKNOWN_CAPABILITY,
                details=f"No capability matches Action: {intent.action.name}"
            )
            self.event_bus.publish("EXECUTION_PLAN_FAILED", source="RuntimeKernel", payload={"event": failure})
            return
            
        # Emit resolved event
        resolved_event = CapabilityResolvedEvent(
            intent_id=intent.session_id,
            manifest_id=manifest.id,
            timestamp=time.time()
        )
        self.event_bus.publish("CAPABILITY_RESOLVED", source="RuntimeKernel", payload={"event": resolved_event})
        
        # 2. Plan Generation
        plan, failure_reason = self.planner.plan(intent, manifest)
        
        if failure_reason:
            logger.error(f"Kernel Failed: {failure_reason.name}")
            failure = PlanFailedEvent(
                intent_id=intent.session_id,
                reason=failure_reason,
                details=f"Planner failed to satisfy parameters for {manifest.id}"
            )
            self.event_bus.publish("EXECUTION_PLAN_FAILED", source="RuntimeKernel", payload={"event": failure})
            return
            
        # Embed the plan in the Kernel state to wait for completion
        # Normally this would be a proper state machine
        if not hasattr(self, 'active_workflows'):
            self.active_workflows = {}
        self.active_workflows[plan.intent_id] = plan
        
        # Pass to execution scheduler
        if hasattr(self, 'scheduler'):
            self.scheduler.schedule_plan(plan)
            
    def handle_capability_completed(self, event: Dict[str, Any]) -> None:
        payload = event.get("payload", {}).get("event")
        if not payload: return
        
        logger.info(f"Kernel received CAPABILITY_COMPLETED for step {payload.context.step_id}. Initiating Verification.")
        if hasattr(self, 'verification_runtime'):
            self.verification_runtime.verify_step(payload.context, payload.status)
            
    def handle_verification_completed(self, event: Dict[str, Any]) -> None:
        payload = event.get("payload", {}).get("event")
        if not payload: return
        
        logger.info(f"Kernel received VERIFICATION_COMPLETED. Status: {payload.status.name}. Finalizing Workflow.")
        
        from desktop.models.execution_models import WorkflowCompletedEvent
        wf_event = WorkflowCompletedEvent(
            intent_id=payload.context.workflow_id,
            plan_id=payload.context.plan_id if hasattr(payload.context, 'plan_id') else "plan-unknown",
            status=payload.status,
            timestamp=time.time()
        )
        self.event_bus.publish("WORKFLOW_COMPLETED", source="RuntimeKernel", payload={"event": wf_event})
        
        # Route to Presentation Runtime
        if hasattr(self, 'presentation_runtime'):
            self.presentation_runtime.handle_verification_completed(event)

