import logging
from typing import Dict, Set
from desktop.character.behavior.state.character_state import CharacterState

logger = logging.getLogger(__name__)

class BehaviorStateMachine:
    """
    S34B: Canonical State Machine validating Character State transitions.
    """
    VALID_TRANSITIONS: Dict[CharacterState, Set[CharacterState]] = {
        CharacterState.BOOT: {CharacterState.WAKE, CharacterState.SLEEP, CharacterState.EDGE_DOT},
        CharacterState.WAKE: {CharacterState.GREETING, CharacterState.LISTENING, CharacterState.THINKING, CharacterState.TALKING, CharacterState.WORKING, CharacterState.SLEEP, CharacterState.EDGE_DOT},
        CharacterState.GREETING: {CharacterState.LISTENING, CharacterState.THINKING, CharacterState.TALKING, CharacterState.WORKING, CharacterState.SLEEP, CharacterState.EDGE_DOT},
        CharacterState.LISTENING: {CharacterState.THINKING, CharacterState.TALKING, CharacterState.WORKING, CharacterState.WARNING, CharacterState.SLEEP, CharacterState.EDGE_DOT},
        CharacterState.THINKING: {CharacterState.TALKING, CharacterState.WORKING, CharacterState.SUCCESS, CharacterState.WARNING, CharacterState.SLEEP, CharacterState.EDGE_DOT},
        CharacterState.TALKING: {CharacterState.LISTENING, CharacterState.THINKING, CharacterState.WORKING, CharacterState.SUCCESS, CharacterState.WARNING, CharacterState.SLEEP, CharacterState.EDGE_DOT},
        CharacterState.WORKING: {CharacterState.TALKING, CharacterState.THINKING, CharacterState.SUCCESS, CharacterState.WARNING, CharacterState.SLEEP, CharacterState.EDGE_DOT},
        CharacterState.SUCCESS: {CharacterState.TALKING, CharacterState.WORKING, CharacterState.LISTENING, CharacterState.SLEEP, CharacterState.EDGE_DOT},
        CharacterState.WARNING: {CharacterState.TALKING, CharacterState.LISTENING, CharacterState.THINKING, CharacterState.SLEEP, CharacterState.EDGE_DOT},
        CharacterState.SLEEP: {CharacterState.WAKE, CharacterState.EDGE_DOT},
        CharacterState.EDGE_DOT: {CharacterState.WAKE, CharacterState.SLEEP}
    }

    def __init__(self, initial_state: CharacterState = CharacterState.BOOT):
        self._current_state = initial_state

    @property
    def current_state(self) -> CharacterState:
        return self._current_state

    def can_transition(self, target_state: CharacterState) -> bool:
        allowed = self.VALID_TRANSITIONS.get(self._current_state, set())
        return target_state in allowed or target_state == self._current_state

    def transition_to(self, target_state: CharacterState) -> bool:
        if self.can_transition(target_state):
            logger.info(f"[BehaviorStateMachine] State transition: {self._current_state.value} -> {target_state.value}")
            self._current_state = target_state
            return True
        logger.warning(f"[BehaviorStateMachine] Invalid transition requested: {self._current_state.value} -> {target_state.value}")
        return False
