import asyncio
from typing import List, Type, Dict
from dataclasses import dataclass
from desktop.models.lifecycle import IRuntime, RuntimeState
from desktop.models.events import SystemEvent, DomainEvent, KernelShutdownRequest
from desktop.models.interaction import InteractionEnvelope
from desktop.app.context import ServiceRegistry, EventBus, KernelContext
from datetime import datetime

@dataclass
class RuntimeConfiguration:
    inference_provider: str = "llama_cpp"
    model: str = "qwen2.5-1.5b"
    speech_enabled: bool = False
    transport: str = "default"
    use_llm: bool = True

class RuntimeKernel:
    """
    Orchestrates the platform. Policy-neutral and deterministic (Rule 172).
    Owns cancellation and the interaction loop.
    """
    def __init__(self, context: KernelContext, runtimes: List[IRuntime]):
        self.context = context
        self.event_bus = self.context.event_bus
        self.runtimes = runtimes
        self._running = False
        
        # Subscribe to shutdown requests (e.g. from /exit in CLI)
        self.context.event_bus.subscribe(KernelShutdownRequest, self._on_shutdown_request)
        
    async def run(self):
        print("\n[Kernel] Interaction Loop Started.\n")
        self._running = True
        
        try:
            while self._running:
                # Input is pushed directly into the EventBus as InteractionEnvelope by TransportManager.
                # Runtimes subscribe to InteractionEnvelope.
                # So the Kernel just needs to keep the event loop alive.
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            print("\n[Kernel] SIGINT Received. Initiating shutdown sequence...")
            await self.shutdown()
            
    async def _on_shutdown_request(self, event: KernelShutdownRequest):
        print(f"\n[Kernel] Shutdown Requested by {event.source}: {event.metadata.get('reason')}")
        self._running = False # Break the loop
            
    async def shutdown(self):
        print("[Kernel] Shutting down runtimes...")
        import asyncio
        for r in reversed(self.runtimes): # Shutdown in reverse order
            try:
                if hasattr(r, "stop"):
                    res = r.stop()
                    if asyncio.iscoroutine(res):
                        await res
                if hasattr(r, "shutdown"):
                    res = r.shutdown()
                    if asyncio.iscoroutine(res):
                        await res
            except Exception as e:
                print(f"[Kernel] Warning: Error shutting down {r.__class__.__name__}: {e}")
                
        print("[Kernel] Flushing EventBus...")
        await self.context.event_bus.flush_and_stop()
        print("[Kernel] Shutdown complete. Goodbye.")

class BootManager:
    """
    Responsible for the deterministic 3-stage boot sequence.
    """
    def __init__(self, config: Optional[RuntimeConfiguration] = None):
        self.registry = ServiceRegistry()
        self.event_bus = EventBus()
        self.config = config or RuntimeConfiguration()
        self.context = KernelContext(self.registry, self.event_bus, config={})
        self.runtimes: List[IRuntime] = []
        self._runtime_states: Dict[IRuntime, RuntimeState] = {}
        
    def construct(self, runtime_classes: List[Type[IRuntime]]):
        """Phase 1: Instantiate runtimes and resolve dependencies."""
        print("[Boot] Phase 1: Constructing Runtimes...")
        
        # (In reality, topological sort using `r.dependencies` would happen here)
        # For demonstration, we assume they are passed in correct topological order.
        
        for r_class in runtime_classes:
            r = r_class()
            self.runtimes.append(r)
            self._runtime_states[r] = RuntimeState.CREATED
            # Register them if they implement a specific service contract
            # (Done manually in demo for simplicity)
            
    async def initialize(self) -> bool:
        """Phase 2: Initialize with Readiness Barrier and Rollback."""
        print("[Boot] Phase 2: Initializing (Readiness Barrier)...")
        initialized = []
        
        for r in self.runtimes:
            self._runtime_states[r] = RuntimeState.INITIALIZING
            try:
                success = await r.initialize(self.context)
                if not success:
                    raise Exception("Initialization returned False")
                self._runtime_states[r] = RuntimeState.READY
                initialized.append(r)
            except Exception as e:
                print(f"[Boot] ❌ FAILED to initialize {r.__class__.__name__}: {e}")
                self._runtime_states[r] = RuntimeState.FAILED
                
                print("[Boot] ⚠️ Readiness Barrier failed. Rolling back...")
                for init_r in reversed(initialized):
                    await init_r.shutdown()
                return False
                
        print("[Boot] ✅ All runtimes READY.")
        return True
        
    async def start(self) -> RuntimeKernel:
        """Phase 3: Start everything and return the Kernel."""
        print("[Boot] Phase 3: Starting...")
        self.event_bus.start()
        
        for r in self.runtimes:
            self._runtime_states[r] = RuntimeState.STARTING
            await r.start()
            self._runtime_states[r] = RuntimeState.RUNNING
            
        print("[Boot] System Boot Complete.")
        return RuntimeKernel(self.context, self.runtimes)

    def compose_runtimes(self, cap_registry, renderers):
        """Standard production runtime composition."""
        from desktop.runtimes.time_runtime import TimeRuntime
        from desktop.runtimes.memory_runtime import MemoryRuntime
        from desktop.runtimes.planner import PlannerRuntime
        from desktop.runtimes.execution import ExecutionRuntime
        from desktop.runtimes.expression_runtime import ExpressionRuntime
        from desktop.runtimes.activity.tracker import ActivityTrackerRuntime
        from desktop.platform.strategies.deterministic_planner import DeterministicPlannerStrategy
        from desktop.runtimes.presence_runtime import PresenceRuntime

        time_runtime = TimeRuntime()
        mem_runtime = MemoryRuntime()
        presence_runtime = PresenceRuntime()
        
        from desktop.app.memory_contracts import IMemoryService
        self.registry.register(IMemoryService, mem_runtime)
        
        exec_runtime = ExecutionRuntime(cap_registry)
        expr_runtime = ExpressionRuntime(renderers)

        # ---------------------------------------------------------
        # Capability Provider (Sprint 15 DI)
        # ---------------------------------------------------------
        from desktop.runtimes.capability.provider import CapabilityProvider
        
        provider = CapabilityProvider(cap_registry)
        provider.register_all()
        
        # Package manager is disabled for Sprint 15 as per explicit instructions
        # from desktop.runtimes.package_manager_runtime import PackageManagerRuntime
        # package_manager = PackageManagerRuntime(...)
        # ---------------------------------------------------------

        if self.config.use_llm:
            from desktop.platform.inference.inference.gguf_provider import GGUFInferenceProvider
            from desktop.runtimes.inference.runtime import InferenceRuntime
            from desktop.runtimes.ai.runtime import AIRuntime
            from desktop.runtimes.conversation.runtime import ConversationRuntime
            
            provider = GGUFInferenceProvider()
            inference_runtime = InferenceRuntime(self.event_bus, provider)
            ai_runtime = AIRuntime(inference_runtime, cap_registry)
            conv_runtime = ConversationRuntime(self.event_bus, ai_runtime)
            activity_runtime = ActivityTrackerRuntime(mem_runtime)
            
            from desktop.app.capability_contracts import CapabilityCatalog
            catalog = CapabilityCatalog(cap_registry)
            
            # TODO: Integrate LLMPlannerStrategy when fully ready. 
            # For now, LLM is available, but planner remains deterministic to preserve stable testing of capability execution.
            planner_strategy = DeterministicPlannerStrategy(catalog)
            plan_runtime = PlannerRuntime(planner_strategy)
            
            from desktop.runtimes.verification_runtime import VerificationRuntime
            from desktop.runtimes.workflow_runtime import WorkflowRuntime
            
            verification_runtime = VerificationRuntime()
            workflow_runtime = WorkflowRuntime(capability_runtime=exec_runtime, verification_runtime=verification_runtime)
            
            self.runtimes.extend([mem_runtime, conv_runtime, ai_runtime, inference_runtime, activity_runtime, plan_runtime, exec_runtime, verification_runtime, workflow_runtime, expr_runtime, presence_runtime, time_runtime])
        else:
            from desktop.app.capability_contracts import CapabilityCatalog
            catalog = CapabilityCatalog(cap_registry)
            planner_strategy = DeterministicPlannerStrategy(catalog)
            plan_runtime = PlannerRuntime(planner_strategy)
            
            from desktop.runtimes.verification_runtime import VerificationRuntime
            from desktop.runtimes.workflow_runtime import WorkflowRuntime
            
            verification_runtime = VerificationRuntime()
            workflow_runtime = WorkflowRuntime(capability_runtime=exec_runtime, verification_runtime=verification_runtime)
            
            self.runtimes.extend([mem_runtime, plan_runtime, exec_runtime, verification_runtime, workflow_runtime, expr_runtime, presence_runtime, time_runtime])


