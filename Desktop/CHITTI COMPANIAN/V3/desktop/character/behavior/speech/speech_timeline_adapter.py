from desktop.character.behavior.speech.speech_context import SpeechContext
from desktop.character.behavior.timeline.timeline_event import TimelineEvent

class SpeechTimelineAdapter:
    """
    S34B: Adapts SpeechContext timelines into scheduled speech behavior events.
    Contains ZERO phoneme synchronization or lip sync logic.
    """
    def adapt_speech_to_events(self, speech: SpeechContext, base_time: float = 0.0) -> list[TimelineEvent]:
        events = []
        if not speech or speech.total_duration_seconds <= 0:
            return events

        # Initial speech greeting / intro
        intro_dur = min(1.0, speech.total_duration_seconds)
        events.append(TimelineEvent(
            behavior_id="CHR_TALK_NEUTRAL_001",
            behavior_name="TalkingNeutral",
            start_time=base_time,
            duration=intro_dur,
            loop_count=1,
            priority="HIGH",
            interruptible=True
        ))

        curr_t = base_time + intro_dur
        rem_dur = speech.total_duration_seconds - intro_dur

        if rem_dur > 0:
            events.append(TimelineEvent(
                behavior_id="CHR_TALK_EXPLAIN_001",
                behavior_name="TalkingExplain",
                start_time=curr_t,
                duration=rem_dur,
                loop_count=int(rem_dur / 1.2) + 1,
                priority="HIGH",
                interruptible=True
            ))

        return events
