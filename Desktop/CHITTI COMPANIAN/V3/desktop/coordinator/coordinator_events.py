from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class CoordinatorEvent:
    event_type: str
    timestamp: float
    payload: Dict[str, Any] = field(default_factory=dict)

class VisualStateChanged(CoordinatorEvent):
    def __init__(self, timestamp: float, old_state: str, new_state: str):
        super().__init__("VisualStateChanged", timestamp, {"old_state": old_state, "new_state": new_state})

class TimelineScheduled(CoordinatorEvent):
    def __init__(self, timestamp: float, session_id: str, timeline_type: str, item_count: int):
        super().__init__("TimelineScheduled", timestamp, {"session_id": session_id, "timeline_type": timeline_type, "item_count": item_count})

class ConflictResolved(CoordinatorEvent):
    def __init__(self, timestamp: float, conflict_type: str, winning_target: str, yielding_target: str):
        super().__init__("ConflictResolved", timestamp, {"conflict_type": conflict_type, "winning": winning_target, "yielding": yielding_target})

class PolicyChanged(CoordinatorEvent):
    def __init__(self, timestamp: float, old_policy: str, new_policy: str):
        super().__init__("PolicyChanged", timestamp, {"old_policy": old_policy, "new_policy": new_policy})

class RuntimeRecovered(CoordinatorEvent):
    def __init__(self, timestamp: float, runtime_name: str, recovery_status: str):
        super().__init__("RuntimeRecovered", timestamp, {"runtime_name": runtime_name, "status": recovery_status})
