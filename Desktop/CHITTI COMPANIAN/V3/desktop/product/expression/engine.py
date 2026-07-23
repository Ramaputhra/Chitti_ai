from typing import Any
from desktop.models.presentation import AvatarState, AvatarStateChanged
from desktop.models.execution_events import (
    WorkflowStartedEvent, TaskCompletedEvent, WorkflowFailedEvent, WorkflowCompletedEvent
)

class ExpressionEngine:
    """
    Subscribes to ExecutionEvents and translates them into Presentation/Expression states.
    This separates the visual presentation state from the cognitive execution flow.
    """
    def __init__(self, event_bus: Any):
        self._event_bus = event_bus
        
    def start(self):
        self._event_bus.subscribe(WorkflowStartedEvent.__name__, self._on_workflow_started)
        self._event_bus.subscribe(TaskCompletedEvent.__name__, self._on_task_completed)
        self._event_bus.subscribe(WorkflowCompletedEvent.__name__, self._on_workflow_completed)
        self._event_bus.subscribe(WorkflowFailedEvent.__name__, self._on_workflow_failed)

    def _emit_state(self, state: AvatarState):
        self._event_bus.publish(AvatarStateChanged(state=state))
        
    def _on_workflow_started(self, event: WorkflowStartedEvent):
        self._emit_state(AvatarState.OPERATING)
        
    def _on_task_completed(self, event: TaskCompletedEvent):
        # We could map certain task capabilities to specific micro-animations
        self._emit_state(AvatarState.HAPPY)
        
    def _on_workflow_completed(self, event: WorkflowCompletedEvent):
        self._emit_state(AvatarState.IDLE)
        
    def _on_workflow_failed(self, event: WorkflowFailedEvent):
        self._emit_state(AvatarState.ERROR)
