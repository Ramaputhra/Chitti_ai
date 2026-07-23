import time
from typing import List, Optional
from desktop.character.behavior.timeline.behavior_timeline import BehaviorTimeline
from desktop.character.behavior.timeline.timeline_event import TimelineEvent
from desktop.character.behavior.scheduler.behavior_transition_manager import BehaviorTransitionManager
from desktop.character.behavior.scheduler.behavior_resolver import BehaviorResolver
from desktop.character.behavior.speech.speech_timeline_adapter import SpeechTimelineAdapter
from desktop.character.behavior.speech.speech_context import SpeechContext

class BehaviorTimelineBuilder:
    """
    S34B: Constructs a complete, seamless, and resolved BehaviorTimeline.
    Inserts transition clips automatically and resolves conflicts.
    """
    def __init__(self):
        self.transition_mgr = BehaviorTransitionManager()
        self.resolver = BehaviorResolver()
        self.speech_adapter = SpeechTimelineAdapter()

    def build_timeline(
        self,
        timeline_id: str,
        session_id: str,
        raw_events: List[TimelineEvent],
        speech_context: Optional[SpeechContext] = None
    ) -> BehaviorTimeline:
        timeline = BehaviorTimeline(timeline_id=timeline_id, session_id=session_id, created_at=time.time())

        events_to_schedule: List[TimelineEvent] = []
        events_to_schedule.extend(raw_events)

        if speech_context:
            speech_events = self.speech_adapter.adapt_speech_to_events(speech_context, base_time=0.0)
            events_to_schedule.extend(speech_events)

        # Resolve timing overlaps and priority overrides
        resolved_events = self.resolver.resolve_timeline(events_to_schedule)

        # Insert transition clips
        final_events: List[TimelineEvent] = []
        for i, evt in enumerate(resolved_events):
            if i > 0:
                prev_evt = final_events[-1]
                trans = self.transition_mgr.get_transition(
                    prev_evt.behavior_name,
                    evt.behavior_name,
                    start_time=prev_evt.start_time + prev_evt.duration
                )
                if trans:
                    final_events.append(trans)
                    evt.start_time = trans.start_time + trans.duration
            final_events.append(evt)

        for evt in final_events:
            timeline.add_event(evt)

        return timeline
