import threading
import time
from typing import Any, Dict, List

from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.event_recorder import IEventRecorder
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState


class EventRecorder(IEventRecorder):
    def __init__(self, event_bus: IEventBus, logger: ILoggingService) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._history: List[Event] = []
        self._lock = threading.RLock()

    @property
    def name(self) -> str:
        return "EventRecorder"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.event_bus.subscribe_all(self._on_event)
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        with self._lock:
            return {"events_recorded": len(self._history)}

    def _on_event(self, event: Event) -> None:
        if self._state != ServiceState.RUNNING:
            return
        
        # Don't record Voice.AudioFrame continuously or memory will exhaust quickly
        if event.id == "Voice.AudioFrame":
            return
            
        with self._lock:
            self._history.append(event)

    def get_history(self) -> List[Event]:
        with self._lock:
            return list(self._history)

    def clear_history(self) -> None:
        with self._lock:
            self._history.clear()
            self.logger.info("EventRecorder history cleared")

    def replay_history(self) -> None:
        with self._lock:
            events = list(self._history)

        if not events:
            self.logger.warning("No events to replay.")
            return

        self.logger.info(f"Replaying {len(events)} events...")
        for event in events:
            replay_event = Event(
                event_id=event.id,
                source=f"{event.source}_Replay",
                payload=event.payload
            )
            self.event_bus.publish(replay_event)
            # Short sleep to let the pipeline process
            time.sleep(0.05)
