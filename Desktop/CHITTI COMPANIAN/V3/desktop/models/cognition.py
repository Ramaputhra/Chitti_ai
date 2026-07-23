from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from desktop.models.identity import ProjectIdentity
from desktop.models.workflow import ProjectWorkflow, ProjectAssessment
from desktop.models.intent import IntentCandidate, IntentType

class DecisionQuality(Enum):
    CERTAIN = "CERTAIN"
    LIKELY = "LIKELY"
    UNCERTAIN = "UNCERTAIN"
    AMBIGUOUS = "AMBIGUOUS"
    REJECTED = "REJECTED"

class PlanningRoute(Enum):
    DETERMINISTIC = "DETERMINISTIC"
    LLM = "LLM"
    HYBRID = "HYBRID"
    CLARIFICATION = "CLARIFICATION"
    REPLAY = "REPLAY"
    REJECT = "REJECT"

@dataclass
class HybridPlanningPolicy:
    provider_health: str = "READY"
    is_offline: bool = False
    latency_budget_ms: float = 1000.0
    cost_budget_exceeded: bool = False
    session_mode: str = "THOROUGH"

class RetryPolicy(Enum):
    NONE = "NONE"
    STANDARD = "STANDARD"
    EXPONENTIAL = "EXPONENTIAL"

@dataclass
class ExecutionPolicy:
    timeout: float = 30.0
    retry_policy: RetryPolicy = RetryPolicy.NONE

@dataclass
class WorkflowRequest:
    action: str
    correlation_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    policy: ExecutionPolicy = field(default_factory=ExecutionPolicy)

@dataclass
class ApprovalRequirement:
    required: bool = False
    reason: Optional[str] = None

@dataclass
class Intent:
    subtype: str
    query: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationIntent(Intent):
    pass

@dataclass
class SystemIntent(Intent):
    pass

@dataclass
class GreetingIntent(Intent):
    confidence: float = 1.0
    query: str = ""
    def __init__(self, confidence: float = 1.0, query: str = ""):
        super().__init__(subtype="GreetingIntent", query=query)
        self.confidence = confidence

@dataclass
class PendingIntent:
    intent: str
    missing_parameters: List[str] = field(default_factory=list)
    captured_parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    expires_at: str = ""
    workflow_id: str = ""
    correlation_id: str = ""
    clarification_count: int = 0

class ConfidencePolicy(Enum):
    STRICT = "STRICT"
    RELAXED = "RELAXED"

@dataclass
class ExecutionPlan:
    intent: Any = None
    workflows: List[WorkflowRequest] = field(default_factory=list)
    decision_quality: DecisionQuality = DecisionQuality.CERTAIN
    approval: ApprovalRequirement = field(default_factory=ApprovalRequirement)

@dataclass
class PlanningDecision:
    plan: ExecutionPlan = field(default_factory=ExecutionPlan)
    confidence: DecisionQuality = DecisionQuality.CERTAIN
    intent: Any = None
    reasoning: str = ""
    requires_approval: bool = False


@dataclass
class GoalState:
    goal_id: str
    status: str  # ACTIVE, PAUSED, CONTINUED, COMPLETED, ABANDONED
    timestamp: float
    decision_basis: List[str]

@dataclass
class Goal:
    goal_id: str
    intent_type: IntentType
    created_at: float
    state_history: List[GoalState] = field(default_factory=list)
    
    @property
    def current_state(self) -> Optional[GoalState]:
        return self.state_history[-1] if self.state_history else None

@dataclass
class ContinuityAssessment:
    status: str  # CONTINUATION, COMPLETION, PAUSED, NEW
    target_goal_id: Optional[str] = None
    reasoning: List[str] = field(default_factory=list)

@dataclass
class ReasoningContext:
    active_project: ProjectIdentity
    workflow: ProjectWorkflow
    assessment: ProjectAssessment
    intent_candidates: List[IntentCandidate]
    recent_goals: List[Goal] = field(default_factory=list)
    session_metadata: Dict[str, Any] = field(default_factory=dict)
    recent_memory_refs: List[Any] = field(default_factory=list)
    conversation_refs: List[Any] = field(default_factory=list)


class MemoryClass(str, Enum):
    """Memory class priorities for context selection."""
    WORKING_MEMORY = "working_memory"
    RECENT_CONVERSATION = "recent_conversation"
    FACT = "fact"
    EPISODE = "episode"
    SESSION_CONTEXT = "session_context"


@dataclass
class ContextSelectionPolicy:
    """Determines the priority order for including memory classes in context."""
    priority_order: List[MemoryClass] = field(default_factory=lambda: [
        MemoryClass.WORKING_MEMORY,
        MemoryClass.RECENT_CONVERSATION,
        MemoryClass.FACT,
        MemoryClass.EPISODE,
        MemoryClass.SESSION_CONTEXT
    ])


@dataclass
class SelectedContext:
    """Context selected for inclusion in the prompt."""
    working_memory: List[str] = field(default_factory=list)
    recent_messages: List[str] = field(default_factory=list)
    facts: List[str] = field(default_factory=list)
    episodes: List[str] = field(default_factory=list)
    session_context: str = ""
