import asyncio
from datetime import datetime
from typing import List, Type
from desktop.models.lifecycle import IRuntime, HealthState
from desktop.models.events import DomainEvent
from desktop.app.kernel import BootManager
from desktop.app.context import KernelContext

# --- Stub Interfaces & Runtimes ---

class IMemoryService:
    def retrieve_context(self) -> str: pass

class MemoryRuntime(IRuntime, IMemoryService):
    @property
    def dependencies(self): return []
    async def initialize(self, context): 
        print("    [MemoryRuntime] Initializing...")
        context.registry.register(IMemoryService, self)
        return True
    async def start(self): print("    [MemoryRuntime] Started.")
    async def stop(self): print("    [MemoryRuntime] Stopped.")
    def health(self): return HealthState.HEALTHY
    async def shutdown(self): print("    [MemoryRuntime] Shutdown.")
    def retrieve_context(self): return "Memory Context"

class FailingMemoryRuntime(MemoryRuntime):
    async def initialize(self, context):
        print("    [FailingMemoryRuntime] Initializing... FAILING!")
        return False

class PlannerRuntime(IRuntime):
    @property
    def dependencies(self): return [IMemoryService]
    async def initialize(self, context: KernelContext):
        print("    [PlannerRuntime] Initializing...")
        self.context = context
        # Prove DI via Registry (Scenario 4)
        mem = context.registry.resolve(IMemoryService)
        print(f"    [PlannerRuntime] Resolved Memory via DI. Result: {mem.retrieve_context()}")
        return True
    async def start(self): 
        print("    [PlannerRuntime] Started.")
        # Prove EventBus (Scenario 3)
        print("    [PlannerRuntime] Publishing ConversationStarted event...")
        self.context.event_bus.publish(DomainEvent(datetime.now(), "Planner", "Conversation", "Started", {}))
    async def stop(self): print("    [PlannerRuntime] Stopped.")
    def health(self): return HealthState.HEALTHY
    async def shutdown(self): print("    [PlannerRuntime] Shutdown.")

class WorkflowRuntime(IRuntime):
    @property
    def dependencies(self): return []
    async def initialize(self, context: KernelContext):
        print("    [WorkflowRuntime] Initializing...")
        context.event_bus.subscribe(DomainEvent, self.on_event)
        return True
    async def start(self): print("    [WorkflowRuntime] Started.")
    async def stop(self): print("    [WorkflowRuntime] Stopped.")
    def health(self): return HealthState.HEALTHY
    async def shutdown(self): print("    [WorkflowRuntime] Shutdown.")
    
    async def on_event(self, event):
        print(f"    [WorkflowRuntime] Received Event asynchronously: {event.action}")

# --- Scenarios ---

async def scenario_success():
    print("\n=== Scenario 1, 3, 4: Successful Boot, DI, and EventBus ===")
    boot = BootManager()
    boot.construct([MemoryRuntime, PlannerRuntime, WorkflowRuntime])
    success = await boot.initialize()
    assert success
    
    kernel = await boot.start()
    
    # Let async events process
    await asyncio.sleep(0.1)
    
    await kernel.shutdown()

async def scenario_failure():
    print("\n=== Scenario 2: Atomic Rollback on Failure ===")
    boot = BootManager()
    boot.construct([PlannerRuntime, FailingMemoryRuntime])
    success = await boot.initialize()
    assert not success
    print("✅ Rollback successful. Kernel aborted boot.")

async def run_demos():
    print("--- Runtime Kernel & BootManager Verification (Sprint 76) ---")
    await scenario_success()
    await scenario_failure()

if __name__ == "__main__":
    asyncio.run(run_demos())
