from enum import Enum
import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)

class CharacterWindowState(Enum):
    HIDDEN = "Hidden"
    SLIDING_IN = "SlidingIn"
    VISIBLE = "Visible"
    TALKING = "Talking"
    WORKING = "Working"
    SLEEPING = "Sleeping"
    EDGE_DOT = "EdgeDot"
    SLIDING_OUT = "SlidingOut"

class CharacterRuntimeStateMachine:
    """
    S36B: State Machine governing Character Window States and Playback State Transitions.
    """
    VALID_TRANSITIONS: Dict[CharacterWindowState, Set[CharacterWindowState]] = {
        CharacterWindowState.HIDDEN: {CharacterWindowState.SLIDING_IN, CharacterWindowState.VISIBLE},
        CharacterWindowState.SLIDING_IN: {CharacterWindowState.VISIBLE, CharacterWindowState.TALKING, CharacterWindowState.WORKING},
        CharacterWindowState.VISIBLE: {CharacterWindowState.TALKING, CharacterWindowState.WORKING, CharacterWindowState.SLEEPING, CharacterWindowState.EDGE_DOT, CharacterWindowState.SLIDING_OUT},
        CharacterWindowState.TALKING: {CharacterWindowState.VISIBLE, CharacterWindowState.WORKING, CharacterWindowState.SLEEPING, CharacterWindowState.EDGE_DOT, CharacterWindowState.SLIDING_OUT},
        CharacterWindowState.WORKING: {CharacterWindowState.VISIBLE, CharacterWindowState.TALKING, CharacterWindowState.SLEEPING, CharacterWindowState.EDGE_DOT, CharacterWindowState.SLIDING_OUT},
        CharacterWindowState.SLEEPING: {CharacterWindowState.SLIDING_IN, CharacterWindowState.VISIBLE, CharacterWindowState.EDGE_DOT},
        CharacterWindowState.EDGE_DOT: {CharacterWindowState.SLIDING_IN, CharacterWindowState.VISIBLE},
        CharacterWindowState.SLIDING_OUT: {CharacterWindowState.HIDDEN}
    }

    def __init__(self, initial_state: CharacterWindowState = CharacterWindowState.HIDDEN):
        self._state = initial_state

    @property
    def current_state(self) -> CharacterWindowState:
        return self._state

    def can_transition(self, target: CharacterWindowState) -> bool:
        allowed = self.VALID_TRANSITIONS.get(self._state, set())
        return target in allowed or target == self._state

    def transition_to(self, target: CharacterWindowState) -> bool:
        if self.can_transition(target):
            logger.info(f"[CharacterRuntimeStateMachine] {self._state.value} -> {target.value}")
            self._state = target
            return True
        logger.warning(f"[CharacterRuntimeStateMachine] Invalid state transition: {self._state.value} -> {target.value}")
        return False
