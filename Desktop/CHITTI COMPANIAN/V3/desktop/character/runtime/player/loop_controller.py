from dataclasses import dataclass
from typing import Optional

@dataclass
class LoopState:
    loop_type: str  # "LoopForever", "LoopUntilSpeechEnds", "LoopUntilEvent", "LoopFixedCount"
    target_count: int = 1
    current_count: int = 0
    speech_ended: bool = False
    event_triggered: bool = False

class LoopController:
    """
    S36B: Evaluates loop continuation criteria for playing behavior clips.
    """
    def should_continue_loop(self, state: LoopState) -> bool:
        if state.loop_type == "LoopForever":
            return True
        if state.loop_type == "LoopUntilSpeechEnds":
            return not state.speech_ended
        if state.loop_type == "LoopUntilEvent":
            return not state.event_triggered
        if state.loop_type == "LoopFixedCount":
            return state.current_count < state.target_count
        return False
