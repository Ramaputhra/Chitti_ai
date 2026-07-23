from typing import Set, Dict

class BehaviorPolicy:
    """
    S34B: Policy rules defining valid behavior sequences, transitions, and priority overrides.
    """
    ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
        "TalkingPresentation": {"PointScreen", "PointChart", "PointTimeline", "Idle"},
        "SearchingFiles": {"TalkingExplain", "WritingNotes", "Idle"},
        "TypingLaptop": {"TalkingExplain", "ThumbsUp", "Idle"},
        "Listening": {"Thinking", "TalkingNeutral", "Idle"},
        "Thinking": {"TalkingNeutral", "TalkingExplain", "Idle"}
    }

    PRIORITY_LEVELS: Dict[str, int] = {
        "LOW": 1,
        "NORMAL": 2,
        "HIGH": 3,
        "CRITICAL": 4
    }

    def is_transition_allowed(self, current_behavior: str, target_behavior: str) -> bool:
        allowed = self.ALLOWED_TRANSITIONS.get(current_behavior, set())
        return not allowed or target_behavior in allowed or target_behavior == "Idle"

    def compare_priority(self, prio1: str, prio2: str) -> int:
        v1 = self.PRIORITY_LEVELS.get(prio1.upper(), 2)
        v2 = self.PRIORITY_LEVELS.get(prio2.upper(), 2)
        return v1 - v2
