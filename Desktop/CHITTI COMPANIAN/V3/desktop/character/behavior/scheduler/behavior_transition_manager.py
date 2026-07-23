from typing import Optional
from desktop.character.behavior.timeline.timeline_event import TimelineEvent

class BehaviorTransitionManager:
    """
    S34B: Automatically inserts smooth transition clips between distinct state behaviors.
    Never cuts clips abruptly!
    """
    TRANSITION_MAP = {
        ("Idle", "TalkingNeutral"): ("CHR_TRANS_IDLE2TALK_001", "IdleToTalk", 0.5),
        ("Idle", "TalkingExplain"): ("CHR_TRANS_IDLE2TALK_001", "IdleToTalk", 0.5),
        ("TalkingNeutral", "Idle"): ("CHR_TRANS_TALK2IDLE_001", "TalkToIdle", 0.5),
        ("TalkingExplain", "Idle"): ("CHR_TRANS_TALK2IDLE_001", "TalkToIdle", 0.5),
        ("Idle", "Thinking"): ("CHR_TRANS_IDLE2THINK_001", "IdleToThinking", 0.5),
        ("Thinking", "TalkingExplain"): ("CHR_TRANS_THINK2TALK_001", "ThinkingToTalk", 0.5),
        ("TypingLaptop", "TalkingExplain"): ("CHR_TRANS_WORK2TALK_001", "WorkingToTalk", 0.5),
        ("Listening", "TalkingNeutral"): ("CHR_TRANS_LISTEN2TALK_001", "ListeningToTalk", 0.5),
        ("Sleepy", "Idle"): ("CHR_TRANS_SLEEP2WAKE_001", "SleepToWake", 0.5),
        ("Wake", "Idle"): ("CHR_TRANS_WAKE2IDLE_001", "WakeToIdle", 0.5)
    }

    def get_transition(self, from_behavior: str, to_behavior: str, start_time: float) -> Optional[TimelineEvent]:
        key = (from_behavior, to_behavior)
        trans_info = self.TRANSITION_MAP.get(key)
        if trans_info:
            t_id, t_name, dur = trans_info
            return TimelineEvent(
                behavior_id=t_id,
                behavior_name=t_name,
                start_time=start_time,
                duration=dur,
                loop_count=1,
                priority="HIGH",
                interruptible=False,
                blend_mode="CROSSFADE"
            )
        return None
