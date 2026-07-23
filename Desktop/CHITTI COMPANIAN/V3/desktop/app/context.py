import asyncio
from typing import Type, TypeVar, Dict, Any, List, Callable, Awaitable
from dataclasses import dataclass
from desktop.models.events import Event

T = TypeVar('T')

class ServiceRegistry:
    """Provides Dependency Injection for synchronous Request/Response services."""
    def __init__(self):
        self._services: Dict[Type, Any] = {}

    def register(self, interface: Type[T], instance: T):
        self._services[interface] = instance

    def resolve(self, interface: Type[T]) -> T:
        if interface not in self._services:
            raise RuntimeError(f"Service {interface.__name__} not found in registry.")
        return self._services[interface]

class EventBus:
    """Dedicated exclusively to asynchronous broadcast state changes."""
    def __init__(self):
        self._subscribers: Dict[Type, List[Callable[[Event], Awaitable[None]]]] = {}
        self._queue = asyncio.Queue()
        self._running = False
        self._task = None

    def subscribe(self, event_type: Type, handler: Callable[[Event], Awaitable[None]]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, event: Event):
        if self._running:
            self._queue.put_nowait(event)

    async def _process_loop(self):
        while self._running:
            try:
                event = await self._queue.get()
                try:
                    handlers = []
                    for event_type, subs in self._subscribers.items():
                        if isinstance(event_type, str):
                            if type(event).__name__ == event_type:
                                handlers.extend(subs)
                        elif isinstance(event_type, type):
                            if isinstance(event, event_type):
                                handlers.extend(subs)
                                
                    for handler in handlers:
                        try:
                            import inspect
                            if inspect.iscoroutinefunction(handler):
                                await handler(event)
                            else:
                                handler(event)
                        except Exception as e:
                            import traceback
                            print(f"[EventBus] Error in handler for {type(event).__name__}: {e}")
                            traceback.print_exc()
                finally:
                    self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                import traceback
                print(f"[EventBus] Critical Error processing event: {e}")
                traceback.print_exc()

    def start(self):
        self._running = True
        self._task = asyncio.create_task(self._process_loop())

    async def flush_and_stop(self):
        """Called during graceful shutdown."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

@dataclass
class KernelContext:
    """Immutable context passed to all runtimes."""
    registry: ServiceRegistry
    event_bus: EventBus
    config: Dict[str, Any]
    # cancellation_token could go here
