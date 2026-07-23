from typing import Any, Dict

from desktop.platform.shared.interfaces.event_bus import IEventBus
from desktop.platform.shared.interfaces.focus import IVoiceFocusManager
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState


class VoiceFocusManager(IVoiceFocusManager):
    def __init__(self, event_bus: IEventBus, logger: ILoggingService) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._current_requester = None
        self._current_priority = -1

    @property
    def name(self) -> str:
        return "VoiceFocusManager"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {
            "current_requester": self._current_requester,
            "priority": self._current_priority,
        }

    def request_focus(self, requester: str, priority: int) -> bool:
        if priority > self._current_priority:
            if self._current_requester:
                self.logger.info(
                    f"Focus stolen from {self._current_requester} by {requester} (priority {priority})"
                )
            self._current_requester = requester
            self._current_priority = priority
            return True
        return False

    def release_focus(self, requester: str) -> None:
        if self._current_requester == requester:
            self._current_requester = None
            self._current_priority = -1
