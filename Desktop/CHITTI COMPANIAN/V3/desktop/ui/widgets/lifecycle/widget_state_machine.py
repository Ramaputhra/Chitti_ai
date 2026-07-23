from enum import Enum
import logging

logger = logging.getLogger(__name__)

class WidgetLifecycleState(Enum):
    UNLOADED = "Unloaded"
    LOADED = "Loaded"
    BOUND = "Bound"
    ATTACHED = "Attached"
    VISIBLE = "Visible"
    HIDDEN = "Hidden"
    EXPANDED = "Expanded"
    COLLAPSED = "Collapsed"
    DESTROYED = "Destroyed"

class WidgetStateMachine:
    """
    S36D-2: State Machine governing Widget Lifecycle States.
    """
    def __init__(self, initial_state: WidgetLifecycleState = WidgetLifecycleState.UNLOADED):
        self._state = initial_state

    @property
    def current_state(self) -> WidgetLifecycleState:
        return self._state

    def transition_to(self, target: WidgetLifecycleState) -> bool:
        logger.info(f"[WidgetStateMachine] Transitioning Widget State: {self._state.value} -> {target.value}")
        self._state = target
        return True
