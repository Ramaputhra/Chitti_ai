from dataclasses import dataclass, field
from typing import List, Optional
from desktop.character.behavior.timeline.timeline_event import TimelineEvent

@dataclass
class BehaviorTimeline:
    """
    S34B: Canonical Behavior Timeline container.
    Contains ONLY scheduled timeline events and sequence metadata. No rendering logic.
    """
    timeline_id: str
    session_id: str
    events: List[TimelineEvent] = field(default_factory=list)
    created_at: float = 0.0

    def add_event(self, event: TimelineEvent):
        self.events.append(event)
        self.events.sort(key=lambda e: e.start_time)

    def get_event_at(self, timestamp: float) -> Optional[TimelineEvent]:
        for e in self.events:
            if e.start_time <= timestamp < (e.start_time + e.duration):
                return e
        return None

    @property
    def total_duration(self) -> float:
        if not self.events:
            return 0.0
        last = self.events[-1]
        return last.start_time + last.duration

    def print_simulation(self):
        print(f"=== Behavior Timeline Simulation [{self.timeline_id}] ===")
        for e in self.events:
            print(f"{e.start_time:04.1f}s - {(e.start_time + e.duration):04.1f}s | [{e.behavior_id}] {e.behavior_name} (Loop: {e.loop_count}, Prio: {e.priority})")
        print(f"Total Timeline Duration: {self.total_duration:04.1f}s\n")
