from enum import Enum
from typing import Protocol


class AppState(Enum):
    BOOTING = "BOOTING"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    RUNNING = "RUNNING"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    TERMINATED = "TERMINATED"


class ILifecycleManager(Protocol):
    """
    Manages the strict state machine of the application.
    """
    @property
    def current_state(self) -> AppState:
        ...

    def transition_to(self, new_state: AppState) -> None:
        """Transitions the application to a new state and emits an event."""
        ...
