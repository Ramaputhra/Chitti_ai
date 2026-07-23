import asyncio
from datetime import datetime
import logging
from desktop.models.lifecycle import IRuntime, HealthState
from desktop.models.cognition import ExecutionPlan, WorkflowRequest, ApprovalRequirement
from desktop.models.execution import ExecutionContext as LegacyExecutionContext, WorkflowContext, ExecutionStatus as LegacyExecutionStatus
from desktop.app.context import KernelContext
from desktop.runtimes.capability.registry import CapabilityRegistry
from desktop.runtimes.capability.invoker import CapabilityInvoker
from desktop.runtimes.capability.context import CapabilityContext
from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus, ExecutionErrorCode

logger = logging.getLogger(__name__)

class ExecutionRuntime(IRuntime):
    """
    Enforces Execution Plans, Never Modifies Them (Rule 177).
    Invokes Capabilities as the only units of execution (Rule 178).
    Sprint 15 Hardening: Delegated to CapabilityInvoker.
    """
    def __init__(self, registry: CapabilityRegistry, invoker: CapabilityInvoker = None):
        self.registry = registry
        self.invoker = invoker or CapabilityInvoker(registry)
        self.context = None

    @property
    def dependencies(self):
        return []

    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        return True

    def register_component(self, package_id: str, component) -> None:
        """
        Sprint 15: Directory scanning and dynamic registration disabled.
        Strict Dependency Injection is used via CapabilityProvider instead.
        """
        logger.info(f"[ExecutionRuntime] register_component called for {package_id}. Dynamic registration disabled.")

    async def start(self) -> bool:
        logger.info("[ExecutionRuntime] Started. Capability runtime active.")
        return True

    async def stop(self) -> bool:
        logger.info("[ExecutionRuntime] Stopped.")
        return True

    def health(self) -> HealthState:
        return HealthState.HEALTHY

    async def shutdown(self) -> bool:
        return True

    async def _on_plan(self, plan: ExecutionPlan):
        """
        Legacy handler. Per Rule 26, WorkflowRuntime owns orchestration and telemetry.
        """
        pass

    async def _execute_workflow(self, plan: ExecutionPlan, workflow: WorkflowRequest):
        logger.info(f"[Execution] Resolving capability: {workflow.action}")
        import uuid
        import time
        from desktop.models.execution import ExecutionStep
        
        wf_context = WorkflowContext(
            plan_id=getattr(plan, 'plan_id', 'unknown'),
            correlation_id=workflow.correlation_id,
            execution_state=LegacyExecutionStatus.WAITING_APPROVAL,
            started_at=datetime.now()
        )
        
        policy = workflow.policy
        max_attempts = 1
        
        step = ExecutionStep(
            step_id=str(uuid.uuid4()),
            capability_name=workflow.action,
            status=LegacyExecutionStatus.WAITING_APPROVAL,
            start_time=time.time(),
            end_time=0.0,
            parameters=getattr(workflow, "parameters", {}) or {}
        )
        
        for attempt in range(1, max_attempts + 1):
            wf_context.attempt_count = attempt
            step.retries = attempt - 1
            logger.info(f"[Execution] Invoking {workflow.action} (Attempt {attempt}/{max_attempts})...")
            
            # Capability Context Isolation (Least privilege)
            cap_context = CapabilityContext(
                logger=logging.getLogger(f"capability.{workflow.action}"),
                configuration={}, # To be wired in future sprint
                telemetry=None
            )
            
            kwargs = step.parameters
            if not isinstance(kwargs, dict):
                kwargs = {}
                
            try:
                # We use asyncio.wait_for to enforce the Timeout policy
                coro = self.invoker.invoke(workflow.action, kwargs, cap_context)
                result: ExecutionResult = await asyncio.wait_for(coro, timeout=policy.timeout)
                
                legacy_status = LegacyExecutionStatus.SUCCESS if result.status == ExecutionStatus.SUCCESS else LegacyExecutionStatus.FAILED
                
                wf_context.result = result
                wf_context.execution_state = legacy_status
                step.status = legacy_status
                step.output_payload = getattr(result, "output_data", {})
                
                if result.status == ExecutionStatus.SUCCESS:
                    logger.info(f"[Execution] ✅ SUCCESS: {workflow.action}")
                    break
                elif getattr(result, "retryable", False):
                    logger.warning(f"[Execution] ⚠️ RETRYABLE FAILURE: {result.error_message}")
                    step.error_message = getattr(result, "error_message", "Retryable Failure")
                else:
                    logger.error(f"[Execution] ❌ FAILED: {result.error_message}")
                    step.error_message = getattr(result, "error_message", "Failure")
                    break
                    
            except asyncio.TimeoutError:
                wf_context.execution_state = LegacyExecutionStatus.TIMED_OUT
                step.status = LegacyExecutionStatus.TIMED_OUT
                step.error_message = f"Timeout after {policy.timeout}s"
                logger.error(f"[Execution] ⏱️ TIMED OUT after {policy.timeout}s")
                result = ExecutionResult(status=ExecutionStatus.TIMED_OUT, error_message=step.error_message, error_code=ExecutionErrorCode.TIMEOUT)
            except Exception as e:
                wf_context.execution_state = LegacyExecutionStatus.FAILED
                step.status = LegacyExecutionStatus.FAILED
                step.error_message = str(e)
                logger.exception(f"[Execution] ❌ UNHANDLED EXCEPTION: {e}")
                result = ExecutionResult(status=ExecutionStatus.FAILED, error_message=str(e), error_code=ExecutionErrorCode.UNKNOWN_ERROR)
                break
                
        wf_context.finished_at = datetime.now()
        step.end_time = time.time()
        
        return result
