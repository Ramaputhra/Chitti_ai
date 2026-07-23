import asyncio
from desktop.app.kernel import BootManager
from desktop.runtimes.memory import MemoryRuntime
from desktop.platform.inference.memory.dict_provider import DictMemoryProvider
from desktop.app.memory_contracts import IMemoryService
from desktop.platform.strategies.deterministic_planner import DeterministicPlannerStrategy
from desktop.runtimes.planner import PlannerRuntime
from desktop.models.interaction import InteractionEnvelope
from desktop.models.events import PlanCreated
from desktop.models.cognition import ExecutionPlan

async def verify_planner_runtime():
    print("--- Planner Runtime Verification (Sprint 79) ---")
    
    boot = BootManager()
    
    # 1. Setup Dependencies
    provider = DictMemoryProvider()
    mem_runtime = MemoryRuntime(provider)
    
    strategy = DeterministicPlannerStrategy()
    planner_runtime = PlannerRuntime(strategy)
    
    boot.runtimes.extend([mem_runtime, planner_runtime])
    
    # 2. Boot Kernel
    success = await boot.initialize()
    assert success
    kernel = await boot.start()
    
    # 3. Setup a mock listener for the ExecutionPlan (to simulate Execution Runtime)
    captured_plans = []
    async def on_plan(plan: ExecutionPlan):
        captured_plans.append(plan)
    kernel.context.event_bus.subscribe(ExecutionPlan, on_plan)
    
    # 4. Simulate an incoming interaction
    print("\n[Test 1] Interaction -> Planner -> ExecutionPlan")
    interaction = InteractionEnvelope(payload="Hello!")
    
    # Pass it to the planner
    await planner_runtime.process_intent(interaction)
    
    # 5. Verify Memory
    memory: IMemoryService = boot.registry.resolve(IMemoryService)
    history = memory.get_recent_interactions("default_session")
    assert len(history) == 1
    assert history[0].content == "Hello!"
    print("✅ Planner recorded the incoming interaction in Memory (Rule 175)")
    
    # 6. Verify Plan Generation
    assert len(captured_plans) == 1
    plan = captured_plans[0]
    print(f"✅ Planner generated immutable ExecutionPlan: {plan.plan_id}")
    print(f"   - Intent: {type(plan.intent).__name__} ({plan.intent.subtype})")
    print(f"   - Workflows: {len(plan.workflow_requests)}")
    print(f"   - Workflow[0] Action: {plan.workflow_requests[0].action}")
    print(f"   - Approval Requirement: {plan.approval_requirement.name}")
    print(f"   - Planner Version: {plan.planner_version}")
    
    # 7. Test System Command
    print("\n[Test 2] System Intent (/exit)")
    interaction2 = InteractionEnvelope(payload="/exit")
    await planner_runtime.process_intent(interaction2)
    
    assert len(captured_plans) == 2
    plan2 = captured_plans[1]
    print(f"✅ Planner generated System Intent ExecutionPlan")
    print(f"   - Workflow[0] Action: {plan2.workflow_requests[0].action}")
    
    print("\n[Test 3] Shutdown Flush")
    await kernel.shutdown()
    print("✅ System Shutdown")

if __name__ == "__main__":
    asyncio.run(verify_planner_runtime())
