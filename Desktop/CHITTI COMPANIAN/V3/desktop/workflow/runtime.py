import time
import uuid
from pathlib import Path
from typing import Callable
from datetime import datetime, timezone
from desktop.core.runtime import (
    IRuntime, RuntimeMetadata, RuntimePriority, RuntimeTraits,
    HealthPolicy, RestartPolicy, RuntimeState, HealthPayload
)
from desktop.models.events import SystemEvent
from desktop.intent.models import IntentRecognized
from desktop.workflow.models import (
    WorkflowTemplate, WorkflowContext, WorkflowInstance, WorkflowState,
    WorkflowCreated, WorkflowFailed
)
from desktop.workflow.registry import WorkflowTemplateRegistry

from desktop.core.providers import IConfigProvider

class WorkflowRuntime(IRuntime):
    def __init__(self, publish_event: Callable[[SystemEvent], None], config_provider: IConfigProvider):
        self._publish = publish_event
        self.config_provider = config_provider
        self._state = RuntimeState.CREATED
        self._health = HealthPayload(True, self._state, datetime.now(timezone.utc), 0.0)
        self._metadata = RuntimeMetadata(
            runtime_id="WorkflowRuntime",
            api_version="1.0",
            priority=RuntimePriority.HIGH,
            dependencies=["IntentRuntime"],
            traits=RuntimeTraits(background=True),
            health_policy=HealthPolicy(interval_seconds=2.0),
            restart_policy=RestartPolicy.ALWAYS
        )
        self._instance_counter = 0

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
        
    def _generate_instance_id(self) -> str:
        self._instance_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"WF-{timestamp}-{self._instance_counter:04d}"

    async def handle_intent_recognized(self, event: IntentRecognized) -> None:
        if self._state != RuntimeState.RUNNING:
            return
            
        template = self.config_provider.get_workflow(event.intent_id)
        if not template:
            # LLM Synthesis Fallback would go here. For now, fail.
            self._publish(WorkflowFailed(
                instance=WorkflowInstance(
                    instance_id=self._generate_instance_id(),
                    template_id="UNKNOWN",
                    intent_id=event.intent_id,
                    entities=event.entities,
                    state=WorkflowState.FAILED,
                    context=WorkflowContext(),
                    steps=[],
                    created_at=time.time()
                ),
                reason=f"No template found for intent {event.intent_id}"
            ))
            return
            
        instance = WorkflowInstance(
            instance_id=self._generate_instance_id(),
            template_id=template.workflow_id,
            intent_id=event.intent_id,
            entities=event.entities,
            state=WorkflowState.CREATED,
            context=WorkflowContext(language=event.language), # Injecting conversational context
            steps=template.steps.copy(), # Logical steps
            created_at=time.time(),
            source=event.source,
            estimated_complexity="LOW" # Simple deterministic workflow
        )
        
        self._publish(WorkflowCreated(instance=instance))
