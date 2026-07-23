import logging
from typing import Any, Dict

from desktop.models.planner_models import ExecutionPlan
from desktop.models.execution_models import ExecutionContext
from desktop.platform.core.capability_runtime import CapabilityRuntime

logger = logging.getLogger(__name__)

class ExecutionScheduler:
    """
    Takes an ExecutionPlan and manages the invocation of individual ExecutionSteps.
    Rule 38: Workflow orchestration belongs here and the Kernel.
    """
    def __init__(self, capability_runtime: CapabilityRuntime):
        self.capability_runtime = capability_runtime
        # Maps workflow_id to the active plan
        self.active_plans: Dict[str, ExecutionPlan] = {}

    def schedule_plan(self, plan: ExecutionPlan) -> None:
        logger.info(f"ExecutionScheduler received plan {plan.plan_id} for intent {plan.intent_id}")
        self.active_plans[plan.intent_id] = plan
        
        # MVP: Execute the first step sequentially. 
        # Future: Traverse DAG using dependencies.
        if plan.steps:
            self._schedule_step(plan.intent_id, plan.steps[0])
        else:
            logger.warning("ExecutionPlan has no steps.")

    def _schedule_step(self, workflow_id: str, step) -> None:
        context = ExecutionContext(
            workflow_id=workflow_id,
            step_id=step.step_id,
            capability_id=step.capability_id,
            parameters=step.parameters,
            timeout=10.0
        )
        logger.info(f"ExecutionScheduler handing off step {step.step_id} to CapabilityRuntime")
        self.capability_runtime.execute_step(context)
