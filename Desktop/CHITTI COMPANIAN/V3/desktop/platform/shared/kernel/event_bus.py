import logging
from typing import Callable, Dict, List
from desktop.platform.shared.interfaces.event_bus import IEventBus, Event

logger = logging.getLogger(__name__)

class InMemoryEventBus(IEventBus):
    """
    A simple, synchronous, in-memory implementation of the IEventBus interface.
    Provides the communication backbone for the execution architecture.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self._global_subscribers: List[Callable[[Event], None]] = []
        self._is_initialized = False

    def initialize(self) -> None:
        self._is_initialized = True
        logger.info("InMemoryEventBus initialized.")

    def shutdown(self) -> None:
        self._is_initialized = False
        self._subscribers.clear()
        self._global_subscribers.clear()
        logger.info("InMemoryEventBus shut down.")

    def publish(self, event: Event) -> None:
        if not self._is_initialized:
            logger.warning(f"EventBus received event {event.id} but is not initialized.")
            return
            
        # Notify specific subscribers
        if event.id in self._subscribers:
            for callback in self._subscribers[event.id]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in subscriber for event {event.id}: {e}")
                    
        # Notify global subscribers
        for callback in self._global_subscribers:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in global subscriber for event {event.id}: {e}")

    def subscribe(self, event_id: str, callback: Callable[[Event], None]) -> None:
        if event_id not in self._subscribers:
            self._subscribers[event_id] = []
        if callback not in self._subscribers[event_id]:
            self._subscribers[event_id].append(callback)

    def subscribe_all(self, callback: Callable[[Event], None]) -> None:
        if callback not in self._global_subscribers:
            self._global_subscribers.append(callback)

    def unsubscribe(self, event_id: str, callback: Callable[[Event], None]) -> None:
        if event_id in self._subscribers and callback in self._subscribers[event_id]:
            self._subscribers[event_id].remove(callback)
            
    def subscribe_once(self, event_id: str, callback: Callable[[Event], None]) -> None:
        def wrapper(event: Event):
            self.unsubscribe(event_id, wrapper)
            callback(event)
        self.subscribe(event_id, wrapper)
