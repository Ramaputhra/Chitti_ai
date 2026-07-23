import threading
import time
from collections import defaultdict
from typing import Callable, Dict, List

from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState


class EventBus(IEventBus):
    """
    Thread-safe synchronous Event Bus.
    Routes Events, Commands, Requests, and Responses.
    
    Created by: Application Bootstrap
    Owned by: ApplicationContext
    Used by: Everything
    Destroyed by: Lifecycle Manager
    """

    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = defaultdict(list)
        self._global_subscribers: List[Callable[[Event], None]] = []
        self._lock = threading.RLock()
        self._once_subscribers: Dict[str, List[Callable[[Event], None]]] = defaultdict(list)

    def initialize(self) -> None:
        self.logger.info("Event Bus initialized")

    def start(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info("Event Bus started")

    def pause(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info("Event Bus paused")

    def resume(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info("Event Bus resumed")

    def recover(self) -> None:
        self.logger.info("Event Bus recovering...")
        with self._lock:
            self._subscribers.clear()
            self._once_subscribers.clear()
            self._global_subscribers.clear()
        self.start()

    def shutdown(self) -> None:
        with self._lock:
            self._subscribers.clear()
            self._once_subscribers.clear()
        self.logger.info("Event Bus shut down")

    def publish(self, event: Event) -> None:
        if self._state != ServiceState.RUNNING:
            self.logger.warning(f"EventBus is {self._state.name}, dropping event: {event.id}")
            return
            
        start_time = time.perf_counter()

        # Log automatically
        if event.id != "Voice.AudioFrame":
            self.logger.event(
                event.id,
                module=event.source,
                event_type=event.type.name,
                priority=event.priority.name,
                correlation_id=event.correlation_id,
            )

        with self._lock:
            # Snapshot the lists to avoid issues if subscribers mutate lists during callback
            subs = list(self._subscribers.get(event.id, []))
            once_subs = list(self._once_subscribers.get(event.id, []))
            global_subs = list(self._global_subscribers)
            
            # Immediately clear one-time subscribers
            if event.id in self._once_subscribers:
                del self._once_subscribers[event.id]

        # Execute callbacks (Exceptions do not crash the bus)
        for callback in subs + global_subs:
            try:
                callback(event)
            except Exception as e:
                self.logger.exception(e, module="EventBus", event_id=event.id, subscriber=str(callback))

        for callback in once_subs:
            try:
                callback(event)
            except Exception as e:
                self.logger.exception(e, module="EventBus", event_id=event.id, subscriber=str(callback))

        duration_ms = (time.perf_counter() - start_time) * 1000
        # self.logger.performance(f"EventBus.publish({event.id})", duration_ms)
        # ^ Uncomment if performance tracking per event is desired.

    def subscribe(self, event_id: str, callback: Callable[[Event], None]) -> None:
        with self._lock:
            if event_id not in self._subscribers:
                self._subscribers[event_id] = []
            if callback not in self._subscribers[event_id]:
                self._subscribers[event_id].append(callback)

    def subscribe_all(self, callback: Callable[[Event], None]) -> None:
        with self._lock:
            if callback not in self._global_subscribers:
                self._global_subscribers.append(callback)

    def unsubscribe(self, event_id: str, callback: Callable[[Event], None]) -> None:
        with self._lock:
            if callback in self._subscribers.get(event_id, []):
                self._subscribers[event_id].remove(callback)
            if callback in self._once_subscribers.get(event_id, []):
                self._once_subscribers[event_id].remove(callback)

    def subscribe_once(self, event_id: str, callback: Callable[[Event], None]) -> None:
        with self._lock:
            if callback not in self._once_subscribers[event_id]:
                self._once_subscribers[event_id].append(callback)
