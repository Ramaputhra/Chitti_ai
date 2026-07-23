from enum import Enum
import logging

logger = logging.getLogger(__name__)

class WindowLifecycleState(Enum):
    CREATED = "Created"
    LOADING = "Loading"
    VISIBLE = "Visible"
    HIDDEN = "Hidden"
    ANIMATING = "Animating"
    DOCKED = "Docked"
    FLOATING = "Floating"
    DESTROYED = "Destroyed"

class RuntimeStateMachine:
    """
    S36D-1: State machine governing Desktop Window Lifecycle states.
    """
    def __init__(self, initial_state: WindowLifecycleState = WindowLifecycleState.CREATED):
        self._state = initial_state

    @property
    def current_state(self) -> WindowLifecycleState:
        return self._state

    def transition_to(self, target: WindowLifecycleState) -> bool:
        logger.info(f"[RuntimeStateMachine] Window State Transition: {self._state.value} -> {target.value}")
        self._state = target
        return True
