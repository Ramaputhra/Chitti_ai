import asyncio
from datetime import datetime
from uuid import uuid4
from desktop.app.kernel import BootManager
from desktop.app.capability_contracts import SimpleCapabilityRegistry
from desktop.runtimes.execution import ExecutionRuntime
from desktop.models.cognition import ExecutionPlan, WorkflowRequest, ExecutionPolicy, RetryPolicy, ApprovalRequirement
from desktop.capabilities.expression import get_expression_capability_descriptor
from desktop.capabilities.flaky import get_flaky_capability_descriptor

def make_plan(action: str, policy: ExecutionPolicy, params: dict, approval: ApprovalRequirement = ApprovalRequirement.NONE) -> ExecutionPlan:
    return ExecutionPlan(
        plan_id=str(uuid4()),
        interaction_id="inter_1",
        session_id="session_1",
        intent=None,
        workflow_requests=[WorkflowRequest(action=action, parameters=params, policy=policy)],
        approval_requirement=approval,
        priority=1,
        planner_version="1.0.0"
    )

async def verify_execution_runtime():
    print("--- Execution Runtime Verification (Sprint 80) ---")
    
    boot = BootManager()
    registry = SimpleCapabilityRegistry()
    registry.register(get_expression_capability_descriptor())
    registry.register(get_flaky_capability_descriptor())
    
    exec_runtime = ExecutionRuntime(registry)
    boot.runtimes.append(exec_runtime)
    
    success = await boot.initialize()
    assert success
    kernel = await boot.start()
    
    event_bus = kernel.context.event_bus

    # Scenario 1: Expression (Success)
    print("\n[Scenario 1] ExpressionCapability (SUCCESS)")
    plan1 = make_plan("ExpressionCapability", ExecutionPolicy(), {"text": "Scenario 1 Success!"})
    event_bus.publish(plan1)
    await asyncio.sleep(0.5)

    # Scenario 2: Retryable Failure -> Success
    print("\n[Scenario 2] FlakyCapability (RETRYABLE -> SUCCESS)")
    policy2 = ExecutionPolicy(retry_policy=RetryPolicy.fixed(max_attempts=3))
    plan2 = make_plan("FlakyCapability", policy2, {"mode": "retryable"})
    event_bus.publish(plan2)
    await asyncio.sleep(2.5) # Allow retries

    # Scenario 3: Timeout
    print("\n[Scenario 3] FlakyCapability (TIMEOUT)")
    policy3 = ExecutionPolicy(timeout=1.0)
    plan3 = make_plan("FlakyCapability", policy3, {"mode": "timeout"})
    event_bus.publish(plan3)
    await asyncio.sleep(1.5)

    # Scenario 4: Waiting Approval (Auto-approved by Runtime for now)
    print("\n[Scenario 4] Waiting Approval")
    plan4 = make_plan("ExpressionCapability", ExecutionPolicy(), {"text": "Approved!"}, ApprovalRequirement.USER_CONFIRMATION)
    event_bus.publish(plan4)
    await asyncio.sleep(0.5)

    # Scenario 5: Missing Capability
    print("\n[Scenario 5] Missing Capability in Registry")
    plan5 = make_plan("UnknownAction", ExecutionPolicy(), {})
    event_bus.publish(plan5)
    await asyncio.sleep(0.5)

    await kernel.shutdown()

if __name__ == "__main__":
    asyncio.run(verify_execution_runtime())
