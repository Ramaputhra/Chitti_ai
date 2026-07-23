import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from desktop.platform.shared.models.attention import AttentionEvent


@dataclass
class TemporalContext:
    """Consolidated temporal awareness to avoid repetitive calculations."""
    current_time: float = field(default_factory=time.time)
    time_of_day: str = "Day"
    is_weekend: bool = False
    is_working_hours: bool = True
    upcoming_events: List[str] = field(default_factory=list)
    idle_duration: float = 0.0


@dataclass
class ExecutionState:
    """Current state of the Execution Runtime for interruption evaluation."""
    current_task: Optional[str] = None
    task_progress: float = 0.0
    blocking_resources: List[str] = field(default_factory=list)
    estimated_completion: float = 0.0
    interruptible: bool = True
    criticality: str = "Low"


@dataclass
class WorldState:
    """
    The unified, transient snapshot of the entire system at any given moment.
    Not persisted. Represents the current Situational Awareness for the Planner.
    """
    conversation_state: Dict[str, Any] = field(default_factory=dict)
    desktop_state: Dict[str, Any] = field(default_factory=dict)
    vision_state: Dict[str, Any] = field(default_factory=dict)
    robot_state: Dict[str, Any] = field(default_factory=dict)
    calendar_state: Dict[str, Any] = field(default_factory=dict)
    environment_state: Dict[str, Any] = field(default_factory=dict)
    attention_state: Dict[str, Any] = field(default_factory=dict)
    user_context: Dict[str, Any] = field(default_factory=dict)
    execution_state: ExecutionState = field(default_factory=ExecutionState)
    temporal_context: TemporalContext = field(default_factory=TemporalContext)
    timestamp: float = field(default_factory=time.time)


@dataclass
class WorldStateDiff:
    """
    Represents only the changes between two WorldState snapshots.
    Dramatically reduces Planner workload by supplying only the deltas.
    """
    previous_timestamp: float
    current_timestamp: float
    changes: List[str] = field(default_factory=list)
    new_events: List[AttentionEvent] = field(default_factory=list)
    resolved_events: List[str] = field(default_factory=list)
