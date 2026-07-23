from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class TimelineEvent:
    """
    S34B: Individual Behavior Event scheduled on a BehaviorTimeline.
    Contains ZERO rendering code or PNG frames.
    """
    behavior_id: str
    behavior_name: str
    start_time: float
    duration: float
    loop_count: int = 1  # 0 means infinite loop
    transition_in: Optional[str] = None
    transition_out: Optional[str] = None
    priority: str = "NORMAL"
    interruptible: bool = True
    blend_mode: str = "OVERLAY"
    metadata: Dict[str, Any] = field(default_factory=dict)
