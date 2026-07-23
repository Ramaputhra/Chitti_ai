from desktop.models.events import SystemEvent, EventEnvelope, ContextPayload, EventMetadata
from desktop.core.event_registry import EventOwnershipRegistry
import time
from abc import ABC, abstractmethod
from typing import List, Callable, Dict, Type
import asyncio

class InterceptorAction:
    ALLOW = "ALLOW"
    PAUSE = "PAUSE"
    REJECT = "REJECT"

class IEventInterceptor(ABC):
    @abstractmethod
    def intercept(self, envelope: EventEnvelope) -> str:
        pass

class EventSourceValidator(IEventInterceptor):
    def intercept(self, envelope: EventEnvelope) -> str:
        event_type = getattr(envelope.event, "event_type", type(envelope.event).__name__)
        if not EventOwnershipRegistry.is_authorized(event_type, envelope.metadata.publisher):
            return InterceptorAction.REJECT
        return InterceptorAction.ALLOW

class SchemaValidator(IEventInterceptor):
    def intercept(self, envelope: EventEnvelope) -> str:
        # Validates that the payload structurally matches its definition
        if not hasattr(envelope.event, "event_type"):
            return InterceptorAction.REJECT
        return InterceptorAction.ALLOW

class ContextInjector(IEventInterceptor):
    def intercept(self, envelope: EventEnvelope) -> str:
        if not envelope.context:
            envelope.context = ContextPayload()
        return InterceptorAction.ALLOW

class PolicyInterceptor(IEventInterceptor):
    def intercept(self, envelope: EventEnvelope) -> str:
        if getattr(envelope.event, "requires_authentication", False):
            if envelope.context.authentication != "verified":
                # Pause the workflow instead of dropping it permanently
                return InterceptorAction.PAUSE
        return InterceptorAction.ALLOW

import uuid

class TelemetryInterceptor(IEventInterceptor):
    def intercept(self, envelope: EventEnvelope) -> str:
        envelope.metadata.timestamp = time.time()
        
        # Assign a unique trace_id if none exists, to trace the workflow's entire execution
        if not envelope.metadata.trace_id or envelope.metadata.trace_id == "unknown":
            envelope.metadata.trace_id = f"trace_{uuid.uuid4().hex[:8]}"
            
        return InterceptorAction.ALLOW

class IEventBus(ABC):
    @abstractmethod
    def subscribe(self, event_type: Type[SystemEvent], callback: Callable): pass
    
    @abstractmethod
    async def publish(self, event: SystemEvent, publisher_id: str): pass

class EventBus(IEventBus):
    def __init__(self):
        self._subscribers: Dict[Type[SystemEvent], List[Callable]] = {}
        self._interceptors: List[IEventInterceptor] = [
            EventSourceValidator(),
            SchemaValidator(),
            ContextInjector(),
            PolicyInterceptor(),
            TelemetryInterceptor()
        ]

    def subscribe(self, event_type: Type[SystemEvent], callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    async def publish(self, event: SystemEvent, publisher_id: str):
        envelope = EventEnvelope(event=event, metadata=EventMetadata(publisher=publisher_id))
        
        for interceptor in self._interceptors:
            action = interceptor.intercept(envelope)
            if action == InterceptorAction.REJECT:
                return
            elif action == InterceptorAction.PAUSE:
                # Add to a paused queue to resume later (simplified for now)
                return
                
        callbacks = self._subscribers.get(type(event), [])
        tasks = [asyncio.create_task(cb(envelope)) for cb in callbacks]
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
