from pathlib import Path
from typing import Callable
from datetime import datetime, timezone
from desktop.core.runtime import (
    IRuntime, RuntimeMetadata, RuntimePriority, RuntimeTraits,
    HealthPolicy, RestartPolicy, RuntimeState, HealthPayload
)
from desktop.models.events import SystemEvent
from desktop.workflow.models import WorkflowCreated, WorkflowState, WorkflowValidated, WorkflowReady
from desktop.planner.models import PlannedWorkflow, PlannedStep, WorkflowPlanningStarted, WorkflowPlanningCompleted, PlannerValidationFailed

from desktop.core.providers import IConfigProvider

class PlannerRuntime(IRuntime):
    def __init__(self, publish_event: Callable[[SystemEvent], None], config_provider: IConfigProvider):
        self._publish = publish_event
        self.config_provider = config_provider
        self._state = RuntimeState.CREATED
        self._health = HealthPayload(True, self._state, datetime.now(timezone.utc), 0.0)
        self._metadata = RuntimeMetadata(
            runtime_id="PlannerRuntime",
            api_version="1.0",
            priority=RuntimePriority.HIGH,
            dependencies=["WorkflowRuntime"],
            traits=RuntimeTraits(background=True),
            health_policy=HealthPolicy(interval_seconds=2.0),
            restart_policy=RestartPolicy.ALWAYS
        )

    def get_metadata(self) -> RuntimeMetadata:
        return self._metadata
        
    def get_state(self) -> RuntimeState:
        return self._state
        
    async def initialize(self) -> None:
        self._state = RuntimeState.INITIALIZING
        self._state = RuntimeState.READY
        
    async def start(self) -> None:
        self._state = RuntimeState.RUNNING
        
    async def stop(self) -> None:
        self._state = RuntimeState.STOPPED
        
    async def health_check(self) -> HealthPayload:
        self._health.state = self._state
        self._health.last_heartbeat = datetime.now(timezone.utc)
        return self._health

    async def handle_workflow_created(self, event: WorkflowCreated) -> None:
        if self._state != RuntimeState.RUNNING:
            return
            
        instance = event.instance
        
        # Validation State
        instance.state = WorkflowState.VALIDATED
        self._publish(WorkflowValidated(instance=instance))
        
        # Ready State
        instance.state = WorkflowState.WORKFLOW_READY
        self._publish(WorkflowReady(instance=instance))
        
        # Planning State
        instance.state = WorkflowState.PLANNING
        self._publish(WorkflowPlanningStarted(instance=instance))
        
        # Enrich the workflow (Produces an Immutable PlannedWorkflow object)
        planned_steps = []
        for step in instance.steps:
            if step == "ResolveApplication":
                planned_steps.append(PlannedStep(id="resolve_app", capability="ResolveEntity", params={"type": "application"}))
            elif step == "LaunchApplication":
                planned_steps.append(PlannedStep(id="launch_app", capability="OSExecute", params={"timeout": 30}))
            elif step == "VerifyApplication":
                planned_steps.append(PlannedStep(id="verify_app", capability="OSProcessCheck", params={"retry": 3}))
            else:
                planned_steps.append(PlannedStep(id=step.lower(), capability="Unknown", params={}))
                
        planned_workflow = PlannedWorkflow(
            instance_id=instance.instance_id,
            steps=planned_steps
        )
        
        # Planned State
        instance.state = WorkflowState.PLANNED
        self._publish(WorkflowPlanningCompleted(instance=instance, planned_workflow=planned_workflow))
