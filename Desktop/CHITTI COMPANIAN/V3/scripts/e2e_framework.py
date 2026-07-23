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
from desktop.app.capability_contracts import SimpleCapabilityRegistry
from desktop.packages.productivity_workspace_pack.capabilities.resume_activity import ResumeActivityCapability
from desktop.packages.desktop_pack.capabilities.execution import LaunchApplicationCapability, ExecuteTerminalCommandCapability
from desktop.capabilities.expression import ExpressionCapability
from desktop.app.capability_contracts import ICapability
from desktop.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus

class MockSystemCommandCapability(ICapability):
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        return ExecutionResult(status=ExecutionStatus.SUCCESS, output_data={})

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
        from desktop.app.capability_contracts import CapabilityDescriptor
        # Register capabilities
        self.cap_registry.register(CapabilityDescriptor(id="ResumeActivityCapability", version="1.0", permissions=[], execution_mode="sync", factory=lambda: ResumeActivityCapability()))
        self.cap_registry.register(CapabilityDescriptor(id="LaunchApplicationCapability", version="1.0", permissions=[], execution_mode="sync", factory=lambda: LaunchApplicationCapability()))
        self.cap_registry.register(CapabilityDescriptor(id="ExecuteTerminalCommandCapability", version="1.0", permissions=[], execution_mode="sync", factory=lambda: ExecuteTerminalCommandCapability()))
        self.cap_registry.register(CapabilityDescriptor(id="ExpressionCapability", version="1.0", permissions=[], execution_mode="sync", factory=lambda: ExpressionCapability()))
        self.cap_registry.register(CapabilityDescriptor(id="SystemCommand", version="1.0", permissions=[], execution_mode="sync", factory=lambda: MockSystemCommandCapability()))
        
        self.emitted_events = []
        
        self._original_publish = self.event_bus.publish
        self.event_waiters = []
        
        def intercept_publish(event):
            event_cls = getattr(event.__class__, '__name__', event.__class__.__name__)
            print(f"[EventBus] Published: {event_cls}")
            self.emitted_events.append(event)
            
            # Notify waiters
            for waiter_name, future in self.event_waiters:
                if event_cls == waiter_name and not future.done():
                    future.set_result(event)
                    
            if event_cls == "USER_TRANSCRIPT_GENERATED":
                self._mock_semantic_engine(event)
                
            self._original_publish(event)
            
        self.event_bus.publish = intercept_publish
        
        # Subscribe to USER_TRANSCRIPT_GENERATED to act as the Semantic Engine (deterministic mapping for tests)
        self.event_bus.subscribe("USER_TRANSCRIPT_GENERATED", self._mock_semantic_engine)
        
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
            
    def _mock_semantic_engine(self, event):
        # Convert simulated Whisper text to an Intent
        from desktop.models.cognition import ConversationIntent, SystemIntent
        text = ""
        if hasattr(event, 'payload'):
            text = event.payload.get("text", "").lower()
        elif isinstance(event, dict):
            text = event.get("text", "").lower()
        
        intent = None
        if "resume" in text:
            intent = SystemIntent(subtype="SystemIntent", query="resume_workspace")
            intent.command = "resume_workspace"
        elif "hello" in text:
            intent = ConversationIntent(subtype="GreetingIntent", query=text)
        elif "exit" in text:
            intent = SystemIntent(subtype="SystemIntent", query="shutdown")
            intent.command = "exit"
            
        if intent:
            # Emulate the Planner picking it up
            import asyncio
            asyncio.create_task(self._route_intent(intent))

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
        # V1 runtimes might not all have start(), let's safely call it if it exists
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
