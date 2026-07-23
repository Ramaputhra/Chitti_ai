import heapq
from dataclasses import dataclass, field
from typing import List, Optional
from desktop.character.behavior.timeline.timeline_event import TimelineEvent
from desktop.character.behavior.mapping.behavior_policy import BehaviorPolicy

@dataclass(order=True)
class PrioritizedEvent:
    priority_score: int
    start_time: float
    event: TimelineEvent = field(compare=False)

class BehaviorQueue:
    """
    S34B: Priority queue ordering scheduled timeline events by priority score and start time.
    """
    def __init__(self):
        self._heap: List[PrioritizedEvent] = []
        self._policy = BehaviorPolicy()

    def push(self, event: TimelineEvent):
        score = -self._policy.PRIORITY_LEVELS.get(event.priority.upper(), 2)
        heapq.heappush(self._heap, PrioritizedEvent(priority_score=score, start_time=event.start_time, event=event))

    def pop(self) -> Optional[TimelineEvent]:
        if self._heap:
            return heapq.heappop(self._heap).event
        return None

    def peek(self) -> Optional[TimelineEvent]:
        if self._heap:
            return self._heap[0].event
        return None

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def clear(self):
        self._heap.clear()
