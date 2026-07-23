from typing import Dict, List, Type
from desktop.models.events import SystemEvent

class EventOwnershipRegistry:
    """
    Enforces Rule 244 - Event Ownership.
    Maps Event Type -> Authorized Publisher Runtime ID
    """
    _ownership: Dict[str, str] = {
        # Core & System
        "SystemStartup": "ApplicationCore",
        "SystemShutdown": "ApplicationCore",
        
        # Speech
        "SpeechTranscribed": "SpeechRuntime",
        "SpeakerVerified": "SpeechRuntime",
        
        # Intent
        "IntentRecognized": "IntentRuntime",
        "IntentUnknown": "IntentRuntime",
        
        # Workflow
        "WorkflowCreated": "WorkflowRuntime",
        "WorkflowValidated": "WorkflowRuntime",
        "WorkflowReady": "WorkflowRuntime",
        
        # Planner
        "WorkflowPlanningStarted": "PlannerRuntime",
        "WorkflowPlanningCompleted": "PlannerRuntime",
        "PlannerValidationFailed": "PlannerRuntime",
        
        # Execution Graph
        "ExecutionGraphBuildingStarted": "ExecutionGraphRuntime",
        "ExecutionGraphReady": "ExecutionGraphRuntime",
        "GraphValidationFailed": "ExecutionGraphRuntime",
        "WorkflowReadyForScheduling": "ExecutionGraphRuntime"
    }

    @classmethod
    def get_owner(cls, event_type: str) -> str:
        return cls._ownership.get(event_type, "UNKNOWN")

    @classmethod
    def is_authorized(cls, event_type: str, publisher_id: str) -> bool:
        expected_owner = cls.get_owner(event_type)
        return expected_owner == publisher_id
