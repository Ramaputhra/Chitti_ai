import logging
from typing import Dict, Set
from desktop.voice.runtime.speech_session import SpeechSessionState

logger = logging.getLogger(__name__)

class SpeechStateMachine:
    """
    Validates state transitions for SpeechSession.
    """
    VALID_TRANSITIONS: Dict[SpeechSessionState, Set[SpeechSessionState]] = {
        SpeechSessionState.CREATED: {SpeechSessionState.QUEUED, SpeechSessionState.CANCELLED, SpeechSessionState.FAILED},
        SpeechSessionState.QUEUED: {SpeechSessionState.SYNTHESIZING, SpeechSessionState.CANCELLED, SpeechSessionState.FAILED},
        SpeechSessionState.SYNTHESIZING: {SpeechSessionState.READY, SpeechSessionState.CANCELLED, SpeechSessionState.FAILED},
        SpeechSessionState.READY: {SpeechSessionState.PLAYING, SpeechSessionState.CANCELLED, SpeechSessionState.FAILED},
        SpeechSessionState.PLAYING: {SpeechSessionState.PAUSED, SpeechSessionState.COMPLETED, SpeechSessionState.CANCELLED, SpeechSessionState.FAILED},
        SpeechSessionState.PAUSED: {SpeechSessionState.PLAYING, SpeechSessionState.CANCELLED, SpeechSessionState.FAILED},
        SpeechSessionState.COMPLETED: set(),
        SpeechSessionState.CANCELLED: set(),
        SpeechSessionState.FAILED: set()
    }

    def __init__(self, initial_state: SpeechSessionState = SpeechSessionState.CREATED):
        self._current_state = initial_state

    @property
    def current_state(self) -> SpeechSessionState:
        return self._current_state

    def can_transition(self, target: SpeechSessionState) -> bool:
        allowed = self.VALID_TRANSITIONS.get(self._current_state, set())
        return target in allowed or target == self._current_state

    def transition_to(self, target: SpeechSessionState) -> bool:
        if self.can_transition(target):
            logger.info(f"[SpeechStateMachine] {self._current_state.value} -> {target.value}")
            self._current_state = target
            return True
        logger.warning(f"[SpeechStateMachine] Invalid transition requested: {self._current_state.value} -> {target.value}")
        return False
