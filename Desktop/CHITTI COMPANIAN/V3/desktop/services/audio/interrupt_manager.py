from typing import Any, Dict

from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.interrupt import IInterruptManager
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.interrupt import InterruptReason


class InterruptManager(IInterruptManager):
    def __init__(self, event_bus: IEventBus, logger: ILoggingService) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "InterruptManager"

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
        return {}

    def trigger_interrupt(self, reason: InterruptReason, details: str = "") -> None:
        self.logger.warning(f"Interrupt Triggered: {reason.name} - {details}")
        self.event_bus.publish(
            Event(
                "System.Interrupt",
                self.name,
                {"reason": reason.name, "details": details},
            )
        )
