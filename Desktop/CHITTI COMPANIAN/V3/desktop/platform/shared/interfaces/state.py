from enum import Enum
from typing import Protocol


class SystemState(Enum):
    BOOTING = "BOOTING"
    READY = "READY"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    RESPONDING = "RESPONDING"
    BUSY = "BUSY"
    ERROR = "ERROR"
    SHUTTING_DOWN = "SHUTTING_DOWN"


class IStateManager(Protocol):
    """
    Manages the global operational state of the CHITTI AI.
    Every subsystem queries this instead of inventing local state flags.
    """
    def current_state(self) -> SystemState:
        ...

    def set_state(self, state: SystemState) -> None:
        """Sets the new state and publishes State.Changed."""
        ...
