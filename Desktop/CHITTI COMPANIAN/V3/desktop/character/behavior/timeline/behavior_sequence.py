from dataclasses import dataclass, field
from typing import List
from desktop.character.behavior.timeline.timeline_event import TimelineEvent

@dataclass
class BehaviorSequence:
    """
    S34B: Ordered collection of TimelineEvents representing a composite behavior sequence.
    """
    sequence_id: str
    sequence_name: str
    events: List[TimelineEvent] = field(default_factory=list)

    @property
    def total_duration(self) -> float:
        if not self.events:
            return 0.0
        last = max(self.events, key=lambda e: e.start_time + e.duration)
        return last.start_time + last.duration
