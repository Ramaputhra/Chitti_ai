import time
import uuid
from enum import Enum
from typing import Any, Callable, Dict, Protocol


class EventType(Enum):
    EVENT = "EVENT"
    COMMAND = "COMMAND"
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"


class EventPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class Event:
    """
    Immutable structured event object.
    """
    def __init__(
        self,
        event_id: str,
        source: str,
        payload: Dict[str, Any] | None = None,
        event_type: EventType = EventType.EVENT,
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: str | None = None,
        version: int = 1,
    ) -> None:
        self.id = event_id
        self.source = source
        self.timestamp = time.time()
        self.payload = payload or {}
        self.type = event_type
        self.priority = priority
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.version = version


class IEventBus(Protocol):
    """
    Interface for the CHITTI Event Bus.
    The communication backbone of the system.
    """

    def initialize(self) -> None:
        ...

    def shutdown(self) -> None:
        ...

    def publish(self, event: Event) -> None:
        ...

    def subscribe(self, event_id: str, callback: Callable[[Event], None]) -> None:
        """Subscribes a callback to a specific event_id."""
        ...

    def subscribe_all(self, callback: Callable[[Event], None]) -> None:
        """Subscribes a callback to receive every event passing through the bus."""
        ...

    def unsubscribe(self, event_id: str, callback: Callable[[Event], None]) -> None:
        ...

    def subscribe_once(self, event_id: str, callback: Callable[[Event], None]) -> None:
        ...
