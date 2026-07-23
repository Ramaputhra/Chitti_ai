import enum
from typing import List, Optional
from dataclasses import dataclass, field

class FocusState(enum.Enum):
    FLOW = "flow"
    NORMAL = "normal"
    INTERRUPTED = "interrupted"
    FRACTURED = "fractured"
    RECOVERING = "recovering"

class ContextSwitchType(enum.Enum):
    INTENTIONAL = "intentional"
    INTERRUPTED = "interrupted"
    DISTRACTION = "distraction"
    RESEARCH = "research"
    MULTITASKING = "multitasking"

class InterruptionPolicy(enum.Enum):
    NEVER = "never"       # Simply remember
    PASSIVE = "passive"   # Show only when user opens CHITTI
    SUGGEST = "suggest"   # Small toast
    URGENT = "urgent"     # High disruption acceptable (e.g. data loss)

@dataclass
class Recommendation:
    """A proactive suggestion ranked by the Recommendation Engine."""
    priority: float       # 0.0 to 1.0
    reason: str           # Must be explainable (Rule 139)
    estimated_value: float
    estimated_time: int   # seconds
    confidence: float
    policy: InterruptionPolicy = InterruptionPolicy.PASSIVE

@dataclass
class Bottleneck:
    """Actionable advice for detected friction."""
    reason: str
    duration: int         # seconds
    severity: float
    recommended_action: str

@dataclass
class WorkContinuity:
    """The Planner's favorite object: tracking the macro goal state."""
    last_goal: str
    completion_percentage: float
    resume_point: str
    next_action: str
    supporting_documents: List[str]
    confidence: float

@dataclass
class ContinuityModel:
    """
    The ultimate output of the Work Continuity Capability.
    Answers: What is the most useful thing I can do for the user right now?
    """
    current_focus: FocusState
    unfinished_work: List[WorkContinuity]
    recommended_next_step: Optional[Recommendation]
    blocked_tasks: List[Bottleneck]
    recent_progress: str
    risk_factors: List[str]
    confidence: float
