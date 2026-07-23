from typing import Any, Dict

from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.wake_word import IWakeWordProvider


class MockWakeWordProvider(IWakeWordProvider):
    def __init__(self, event_bus: IEventBus, logger: ILoggingService) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "MockWakeWordProvider"

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

    def start_listening(self) -> None:
        pass

    def stop_listening(self) -> None:
        pass

    def trigger_wake(self) -> None:
        self.logger.info("Mock Wake Word Triggered!")
        self.event_bus.publish(
            Event("Voice.WakeDetected", self.name, {"wake_word": "mock_wake"})
        )
