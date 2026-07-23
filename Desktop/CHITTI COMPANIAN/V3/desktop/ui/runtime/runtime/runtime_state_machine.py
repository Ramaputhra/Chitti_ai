from enum import Enum
import logging

logger = logging.getLogger(__name__)

class UIWindowState(Enum):
    HIDDEN = "Hidden"
    SLIDING_IN = "SlidingIn"
    VISIBLE = "Visible"
    EXPANDED = "Expanded"
    COLLAPSED = "Collapsed"
    DOCKED = "Docked"
    FLOATING = "Floating"
    SLIDING_OUT = "SlidingOut"

class DesktopUIRuntimeStateMachine:
    """
    S36D: State Machine governing Desktop UI Window & Widget Lifecycle States.
    """
    def __init__(self, initial_state: UIWindowState = UIWindowState.HIDDEN):
        self._state = initial_state

    @property
    def current_state(self) -> UIWindowState:
        return self._state

    def transition_to(self, target: UIWindowState) -> bool:
        logger.info(f"[DesktopUIRuntimeStateMachine] State Transition: {self._state.value} -> {target.value}")
        self._state = target
        return True
