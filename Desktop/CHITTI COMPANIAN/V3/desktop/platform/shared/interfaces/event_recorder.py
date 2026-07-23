from typing import List

from desktop.platform.shared.interfaces.event_bus import Event
from desktop.platform.shared.interfaces.service import IService


class IEventRecorder(IService):
    """
    Subscribes to all events on the EventBus for tracing and replays.
    """
    def get_history(self) -> List[Event]:
        ...

    def clear_history(self) -> None:
        ...

    def replay_history(self) -> None:
        """
        Takes the current history and publishes it sequentially back onto the bus.
        Useful for simulating conversations without talking.
        """
        ...
