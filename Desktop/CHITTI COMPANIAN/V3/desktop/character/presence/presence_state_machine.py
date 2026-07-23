import logging
from typing import Dict, Set
from desktop.character.presence.presence_events import PresenceStateEnum

logger = logging.getLogger(__name__)

class PresenceStateMachine:
    """
    S36E: State Machine governing Character Presence Lifecycle States:
    SYSTEM_TRAY -> WAKE -> CHARACTER_WINDOW -> PRESENCE_DOT -> SYSTEM_TRAY.
    Background Runtime remains active in EVERY state.
    """
    VALID_TRANSITIONS: Dict[PresenceStateEnum, Set[PresenceStateEnum]] = {
        PresenceStateEnum.SYSTEM_TRAY: {PresenceStateEnum.WAKE, PresenceStateEnum.CHARACTER_WINDOW},
        PresenceStateEnum.WAKE: {PresenceStateEnum.CHARACTER_WINDOW, PresenceStateEnum.PRESENCE_DOT, PresenceStateEnum.SYSTEM_TRAY},
        PresenceStateEnum.CHARACTER_WINDOW: {PresenceStateEnum.PRESENCE_DOT, PresenceStateEnum.SYSTEM_TRAY, PresenceStateEnum.WAKE},
        PresenceStateEnum.PRESENCE_DOT: {PresenceStateEnum.CHARACTER_WINDOW, PresenceStateEnum.SYSTEM_TRAY, PresenceStateEnum.WAKE}
    }

    def __init__(self, initial_state: PresenceStateEnum = PresenceStateEnum.SYSTEM_TRAY):
        self._state = initial_state

    @property
    def current_state(self) -> PresenceStateEnum:
        return self._state

    def can_transition(self, target: PresenceStateEnum) -> bool:
        allowed = self.VALID_TRANSITIONS.get(self._state, set())
        return target in allowed or target == self._state

    def transition_to(self, target: PresenceStateEnum) -> bool:
        if self.can_transition(target):
            logger.info(f"[PresenceStateMachine] Presence Transition: {self._state.value} -> {target.value}")
            self._state = target
            return True
        logger.warning(f"[PresenceStateMachine] Invalid Presence Transition: {self._state.value} -> {target.value}")
        return False
