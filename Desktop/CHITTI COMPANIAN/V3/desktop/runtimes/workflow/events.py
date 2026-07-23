from typing import Any, Dict
from desktop.platform.shared.interfaces.event_bus import Event

class WorkflowStarted(Event):
    def __init__(self, workflow_id: str, intent: str):
        super().__init__(
            event_id="Workflow.Started",
            source="WorkflowRuntime",
            payload={"workflow_id": workflow_id, "intent": intent}
        )

class WorkflowCompleted(Event):
    def __init__(self, workflow_id: str):
        super().__init__(
            event_id="Workflow.Completed",
            source="WorkflowRuntime",
            payload={"workflow_id": workflow_id}
        )

class WorkflowFailed(Event):
    def __init__(self, workflow_id: str, error: str):
        super().__init__(
            event_id="Workflow.Failed",
            source="WorkflowRuntime",
            payload={"workflow_id": workflow_id, "error": error}
        )

class WorkflowCancelled(Event):
    def __init__(self, workflow_id: str):
        super().__init__(
            event_id="Workflow.Cancelled",
            source="WorkflowRuntime",
            payload={"workflow_id": workflow_id}
        )

class StepStarted(Event):
    def __init__(self, workflow_id: str, step_id: str, action: str):
        super().__init__(
            event_id="Workflow.StepStarted",
            source="WorkflowRuntime",
            payload={"workflow_id": workflow_id, "step_id": step_id, "action": action}
        )

class StepCompleted(Event):
    def __init__(self, workflow_id: str, step_id: str, action: str, result: Dict[str, Any]):
        super().__init__(
            event_id="Workflow.StepCompleted",
            source="WorkflowRuntime",
            payload={"workflow_id": workflow_id, "step_id": step_id, "action": action, "result": result}
        )

class StepFailed(Event):
    def __init__(self, workflow_id: str, step_id: str, action: str, error: str):
        super().__init__(
            event_id="Workflow.StepFailed",
            source="WorkflowRuntime",
            payload={"workflow_id": workflow_id, "step_id": step_id, "action": action, "error": error}
        )
