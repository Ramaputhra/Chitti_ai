from typing import List
from desktop.character.behavior.timeline.timeline_event import TimelineEvent
from desktop.character.behavior.mapping.behavior_policy import BehaviorPolicy

class BehaviorResolver:
    """
    S34B: Resolves timeline event collisions, overlaps, and priority overrides.
    """
    def __init__(self):
        self.policy = BehaviorPolicy()

    def resolve_timeline(self, events: List[TimelineEvent]) -> List[TimelineEvent]:
        if not events:
            return []

        sorted_events = sorted(events, key=lambda e: e.start_time)
        resolved: List[TimelineEvent] = []

        for evt in sorted_events:
            if not resolved:
                resolved.append(evt)
                continue

            last = resolved[-1]
            last_end = last.start_time + last.duration

            if evt.start_time < last_end:
                cmp = self.policy.compare_priority(evt.priority, last.priority)
                if cmp > 0 and last.interruptible:
                    # Truncate previous event to fit higher priority event
                    last.duration = max(0.1, evt.start_time - last.start_time)
                    resolved.append(evt)
                else:
                    # Delay lower/equal priority event after current event
                    evt.start_time = last_end
                    resolved.append(evt)
            else:
                resolved.append(evt)

        return resolved
