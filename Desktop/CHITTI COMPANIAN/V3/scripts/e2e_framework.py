import sys
import os
import asyncio
from typing import Optional, List

from desktop.app.context import EventBus, KernelContext, ServiceRegistry
from desktop.app.kernel import RuntimeKernel
from desktop.runtimes.memory_runtime import MemoryRuntime
from desktop.runtimes.planner import PlannerRuntime
from desktop.platform.strategies.deterministic_planner import DeterministicPlannerStrategy
from desktop.runtimes.execution import ExecutionRuntime
from desktop.app.capability_contracts import SimpleCapabilityRegistry, CapabilityDescriptor, CapabilityExecutionMode
from desktop.packages.productivity_workspace_pack.capabilities.resume_activity import ResumeActivityCapability
from desktop.packages.desktop_pack.capabilities.execution import LaunchApplicationCapability, ExecuteTerminalCommandCapability
from desktop.capabilities.expression import ExpressionCapability
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus


class MockSystemCommandCapability(ICapability):
    def __init__(self):
        self._state = "stopped"
    
    @property
    def name(self) -> str:
        return "MockSystemCommandCapability"
    
    @property
    def capability_id(self) -> str:
        return "system_command"
    
    async def initialize(self) -> None:
        self._state = "running"
    
    async def shutdown(self) -> None:
        self._state = "stopped"
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        return ExecutionResult(status=ExecutionStatus.SUCCESS, data={})


class MockEvent:
    def __init__(self, name, source="", payload=None):
        self.name = name
        self.source = source
        self.payload = payload or {}
    @property
    def __class__(self):
        class Dummy:
            __name__ = self.name
        return Dummy()


class HeadlessTestHost:
    """
    Simulates the RuntimeKernel for E2E testing without a UI.
    Provides utility methods to assert events.
    """
    def __init__(self):
        self.registry = ServiceRegistry()
        self.event_bus = EventBus()
        self.registry.register(EventBus, self.event_bus)
        self.context = KernelContext(self.registry, self.event_bus, {})
        
        self.cap_registry = SimpleCapabilityRegistry()
        # Register capabilities with correct CapabilityExecutionMode enum
        self.cap_registry.register(CapabilityDescriptor(
            id="ResumeActivityCapability", version="1.0", permissions=[], 
            execution_mode=CapabilityExecutionMode.ASYNC, 
            factory=lambda: ResumeActivityCapability()
        ))
        self.cap_registry.register(CapabilityDescriptor(
            id="LaunchApplicationCapability", version="1.0", permissions=[], 
            execution_mode=CapabilityExecutionMode.ASYNC, 
            factory=lambda: LaunchApplicationCapability()
        ))
        self.cap_registry.register(CapabilityDescriptor(
            id="ExecuteTerminalCommandCapability", version="1.0", permissions=[], 
            execution_mode=CapabilityExecutionMode.ASYNC, 
            factory=lambda: ExecuteTerminalCommandCapability()
        ))
        self.cap_registry.register(CapabilityDescriptor(
            id="ExpressionCapability", version="1.0", permissions=[], 
            execution_mode=CapabilityExecutionMode.ASYNC, 
            factory=lambda: ExpressionCapability()
        ))
        self.cap_registry.register(CapabilityDescriptor(
            id="SystemCommand", version="1.0", permissions=[], 
            execution_mode=CapabilityExecutionMode.ASYNC, 
            factory=lambda: MockSystemCommandCapability()
        ))
        
        self.emitted_events = []
        
        self._original_publish = self.event_bus.publish
        self.event_waiters = []
        
        def intercept_publish(event):
            event_cls = getattr(event.__class__, '__name__', event.__class__.__name__)
            print(f"[EventBus] Published: {event_cls}")
            self.emitted_events.append(event)
            
            # Notify waiters
            for waiter_name, future in list(self.event_waiters):
                if event_cls == waiter_name and not future.done():
                    future.set_result(event)
                    self.event_waiters.remove((waiter_name, future))
                    
            if event_cls == "USER_TRANSCRIPT_GENERATED":
                asyncio.create_task(self._mock_semantic_engine_async(event))
                
            self._original_publish(event)
            
        self.event_bus.publish = intercept_publish
        
        self.memory_runtime = MemoryRuntime()
        self.planner_runtime = PlannerRuntime(strategy=DeterministicPlannerStrategy())
        self.execution_runtime = ExecutionRuntime(self.cap_registry)
    
    async def wait_for_event(self, event_name: str, timeout: float = 5.0):
        """Asynchronously wait for an event to be published."""
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        
        # Check if already emitted
        for event in self.emitted_events:
            if getattr(event.__class__, '__name__', event.__class__.__name__) == event_name:
                return event
                
        self.event_waiters.append((event_name, future))
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            return None
            
    async def _mock_semantic_engine_async(self, event):
        # Convert simulated Whisper text to an Intent and emit ExpressionRequested
        from desktop.models.events import Event
        
        text = ""
        if hasattr(event, 'payload'):
            text = event.payload.get("text", "").lower()
        elif isinstance(event, dict):
            text = event.get("text", "").lower()
        
        # For greeting, emit ExpressionRequested event
        if "hello" in text:
            # Create and emit ExpressionRequested event
            from dataclasses import dataclass
            @dataclass
            class ExpressionRequested:
                event_type: str
                source: str
                payload: dict
            
            expr_event = ExpressionRequested(
                event_type="ExpressionRequested",
                source="ExpressionRuntime",
                payload={"expression_type": "greeting", "text": "Hello, how can I help you?"}
            )
            self.event_bus.publish(expr_event)
        
        # Route other intents
        from desktop.models.cognition import SystemIntent
        intent = None
        if "resume" in text:
            intent = SystemIntent(subtype="SystemIntent", query="resume_workspace")
            intent.command = "resume_workspace"
        elif "exit" in text:
            intent = SystemIntent(subtype="SystemIntent", query="shutdown")
            intent.command = "exit"
            
        if intent:
            await self._route_intent(intent)

    async def _route_intent(self, intent):
        try:
            from desktop.models.memory import MemorySnapshot
            snapshot = MemorySnapshot(session_id="test", workflow_id="test", records=[], working_memory={})
            decision = self.planner_runtime.strategy.formulate_decision(intent, snapshot)
            if decision and decision.plan:
                if hasattr(self.execution_runtime, '_on_plan'):
                    await self.execution_runtime._on_plan(decision.plan)
                elif hasattr(self.execution_runtime, 'execute_plan'):
                    await self.execution_runtime.execute_plan(decision.plan)
        except Exception as e:
            print(f"[_route_intent Error] {repr(e)}")
            import traceback
            traceback.print_exc()
    
    async def start(self):
        await self.memory_runtime.initialize(self.context)
        await self.planner_runtime.initialize(self.context)
        await self.execution_runtime.initialize(self.context)
        
        await self.memory_runtime.start()
        if hasattr(self.planner_runtime, 'start'):
            await self.planner_runtime.start()
        if hasattr(self.execution_runtime, 'start'):
            await self.execution_runtime.start()
        
    async def stop(self):
        if hasattr(self.memory_runtime, 'stop'):
            await self.memory_runtime.stop()
        if hasattr(self.planner_runtime, 'stop'):
            await self.planner_runtime.stop()
        if hasattr(self.execution_runtime, 'stop'):
            await self.execution_runtime.stop()
        
    def assert_event_emitted(self, event_name: str) -> bool:
        """Returns True if an event with the given class name was emitted."""
        for event in self.emitted_events:
            if getattr(event.__class__, '__name__', event.__class__.__name__) == event_name:
                return True
        return False
        
    def get_event(self, event_name: str):
        for event in self.emitted_events:
            if getattr(event.__class__, '__name__', event.__class__.__name__) == event_name:
                return event
        return None
