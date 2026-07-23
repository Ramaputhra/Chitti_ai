import threading
import time
from typing import Any

from desktop.platform.shared.interfaces.event_bus import Event, EventPriority, EventType
from desktop.platform.integrations.core.event_bus import EventBus


class MockLogger:
    def info(self, msg: str, **kwargs: Any) -> None: pass
    def warning(self, msg: str, **kwargs: Any) -> None: pass
    def event(self, event_id: str, module: str, **kwargs: Any) -> None: pass
    def exception(self, exc: Exception, **kwargs: Any) -> None: pass


def test_event_bus_subscribe() -> None:
    bus = EventBus(MockLogger())  # type: ignore
    bus.start()
    received = []

    def handler(evt: Event) -> None:
        received.append(evt)

    bus.subscribe("Test.Event", handler)
    bus.publish(Event("Test.Event", source="Test"))

    assert len(received) == 1
    assert received[0].id == "Test.Event"


def test_event_bus_subscribe_once() -> None:
    bus = EventBus(MockLogger())  # type: ignore
    bus.start()
    received = []

    def handler(evt: Event) -> None:
        received.append(evt)

    bus.subscribe_once("Test.Event", handler)
    
    bus.publish(Event("Test.Event", source="Test"))
    bus.publish(Event("Test.Event", source="Test"))

    assert len(received) == 1


def test_event_bus_unsubscribe() -> None:
    bus = EventBus(MockLogger())  # type: ignore
    bus.start()
    received = []

    def handler(evt: Event) -> None:
        received.append(evt)

    bus.subscribe("Test.Event", handler)
    bus.unsubscribe("Test.Event", handler)
    
    bus.publish(Event("Test.Event", source="Test"))
    assert len(received) == 0


def test_event_bus_exception_isolation() -> None:
    bus = EventBus(MockLogger())  # type: ignore
    bus.start()
    received = []

    def bad_handler(evt: Event) -> None:
        raise ValueError("Crash")

    def good_handler(evt: Event) -> None:
        received.append(evt)

    bus.subscribe("Test.Event", bad_handler)
    bus.subscribe("Test.Event", good_handler)

    bus.publish(Event("Test.Event", source="Test"))
    
    assert len(received) == 1


def test_event_bus_thread_safety() -> None:
    bus = EventBus(MockLogger())  # type: ignore
    bus.start()
    received = []

    def handler(evt: Event) -> None:
        received.append(evt)

    bus.subscribe("Test.Event", handler)

    def worker() -> None:
        for _ in range(100):
            bus.publish(Event("Test.Event", source="Thread"))

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(received) == 1000


def test_event_bus_performance() -> None:
    bus = EventBus(MockLogger())  # type: ignore
    bus.start()
    
    def handler(evt: Event) -> None:
        pass

    for _ in range(100):
        bus.subscribe("Perf.Event", handler)

    start = time.perf_counter()
    bus.publish(Event("Perf.Event", source="PerfTest"))
    duration_ms = (time.perf_counter() - start) * 1000

    # Ensure it publishes to 100 subscribers in less than 5ms
    assert duration_ms < 5.0
