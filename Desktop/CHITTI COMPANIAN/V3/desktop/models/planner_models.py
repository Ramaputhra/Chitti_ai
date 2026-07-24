from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
import uuid

class PlanFailureReason(Enum):
    UNKNOWN_CAPABILITY = "UNKNOWN_CAPABILITY"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INVALID_INTENT = "INVALID_INTENT"
    AMBIGUOUS_TARGET = "AMBIGUOUS_TARGET"
    DEPENDENCY_FAILED = "DEPENDENCY_FAILED"

@dataclass
class ExecutionGoal:
    domain: str
    action: str
    target: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class CapabilityResolution:
    capability: str
    confidence: float
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowStep:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    capability: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    verification_policy: str = "default"
    timeout: int = 30
    retry_policy: str = "default"
    rollback_policy: str = "none"
    presentation_hint: str = "normal"
    dependencies: List[str] = field(default_factory=list) # step_ids this step depends on

@dataclass
class WorkflowPlan:
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goal_id: str = "" # Maps back to ExecutionGoal/Session
    version: int = 1
    steps: List[WorkflowStep] = field(default_factory=list)

# Aliases for backward compatibility
ExecutionPlan = WorkflowPlan
ExecutionStep = WorkflowStep

@dataclass
class CapabilityResolvedEvent:
    intent_id: str
    manifest_id: str
    timestamp: float

@dataclass
class WorkflowPlanCreatedEvent:
    plan: WorkflowPlan
    timestamp: float

@dataclass
class PlanFailedEvent:
    intent_id: str
    reason: PlanFailureReason
    details: str
