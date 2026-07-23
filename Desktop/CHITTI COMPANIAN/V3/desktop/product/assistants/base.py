from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

class AutonomyLevel(Enum):
    OBSERVE_MORE = 0             # Current evidence insufficient. Need more context.
    SUGGEST = 1                  # I found a bug
    ASK = 2                      # Shall I fix it?
    EXECUTE_WITH_APPROVAL = 3    # Ready to modify 3 files (Produces Workflow)
    AUTONOMOUS = 4               # Only for reversible, trusted ops

@dataclass
class Evidence:
    """Structured evidence for explainability."""
    type: str
    source: str
    confidence: float
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Explanation:
    """Every recommendation must include Evidence, Confidence, and Workflow (Rule 142)."""
    reason: str
    evidence: List[Evidence]
    confidence: float
    suggested_workflow: Optional[Any] = None

@dataclass
class AssistantMetrics:
    """Telemetry for optimizing assistant execution."""
    time_to_observe: float = 0.0
    time_to_recall: float = 0.0
    planning_time: float = 0.0
    goal_confidence: float = 0.0
    workflow_nodes: int = 0
    tokens_used: int = 0
    runtime_calls: int = 0

@dataclass
class AssistantContext:
    """
    Immutable context object provided to the assistant.
    Keeps assistants independent of runtime APIs.
    """
    workspace: Any
    memory: Any
    timeline: Any
    user_goal: Any
    confidence: float
    constraints: List[str]
    environment: Dict[str, Any]
    planner_context: Dict[str, Any]

@dataclass
class AssistantResponse:
    goal: str
    autonomy: AutonomyLevel
    explanation: Explanation
    metrics: AssistantMetrics
    payload: Dict[str, Any]

class BaseAssistant(ABC):
    """
    The Product Layer.
    Assistants are stateless orchestrators. They own UX, not infrastructure (Rule 141).
    """
    @abstractmethod
    async def process_intent(self, context: AssistantContext) -> AssistantResponse:
        pass
