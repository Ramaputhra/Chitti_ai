from typing import Any, Dict
from desktop.platform.shared.models.task import TaskStepData
from desktop.platform.shared.models.workflow import Workflow, WorkflowStep, ExecutionPolicy, TimeoutClass
from desktop.platform.shared.models.workflow_actions import WorkflowAction
from desktop.platform.shared.interfaces.logger import ILoggingService

class WorkflowBuilder:
    """
    Safely converts LLM-generated TaskSteps into immutable Workflows.
    Protects the Runtime Kernel from malformed or hallucinated actions (Rule 63).
    """
    def __init__(self, logger: ILoggingService):
        self.logger = logger

    def build(self, step_data: TaskStepData, correlation_id: str = "") -> Workflow:
        """
        Takes a TaskStepData (which has an action_type like 'search', 'read', 'invoke', 'complete')
        and maps it to valid WorkflowStep primitives.
        """
        self.logger.info(f"WorkflowBuilder constructing Workflow for action: {step_data.action_type}")
        steps = []
        
        # Default mapping of generic action types to capabilities
        action_type = step_data.action_type.lower()
        
        if action_type == "search":
            steps.append(WorkflowStep(
                step_id="step_1",
                action=WorkflowAction.INVOKE_CAPABILITY,
                parameters={
                    "capability_id": "SearchCapability",
                    "tool_name": "search",
                    **step_data.parameters
                },
                policy=ExecutionPolicy(timeout_class=TimeoutClass.BACKGROUND)
            ))
        elif action_type == "read":
            steps.append(WorkflowStep(
                step_id="step_1",
                action=WorkflowAction.INVOKE_CAPABILITY,
                parameters={
                    "capability_id": "WebPageCapability",
                    "tool_name": "read_page",
                    **step_data.parameters
                },
                policy=ExecutionPolicy(timeout_class=TimeoutClass.BACKGROUND)
            ))
        elif action_type == "complete":
            # The task orchestrator decided the goal is complete and wants to present an answer
            steps.append(WorkflowStep(
                step_id="step_1",
                action=WorkflowAction.SPEAK,
                parameters={"text": step_data.parameters.get("answer", "Task complete.")}
            ))
        elif action_type == "invoke":
            # Direct capability invocation requested by LLM
            steps.append(WorkflowStep(
                step_id="step_1",
                action=WorkflowAction.INVOKE_CAPABILITY,
                parameters=step_data.parameters,
                policy=ExecutionPolicy(timeout_class=TimeoutClass.INTERACTIVE)
            ))
        else:
            # Fallback for unrecognized action types, default to invoking capability
            self.logger.warning(f"WorkflowBuilder received unknown action_type '{action_type}'. Defaulting to INVOKE_CAPABILITY.")
            steps.append(WorkflowStep(
                step_id="step_1",
                action=WorkflowAction.INVOKE_CAPABILITY,
                parameters=step_data.parameters,
                policy=ExecutionPolicy(timeout_class=TimeoutClass.INTERACTIVE)
            ))
            
        # Topologically link steps if there were multiple (currently there is only one per build)
        for i, step in enumerate(steps):
            if i > 0:
                step.depends_on.append(steps[i-1].step_id)
            
        workflow = Workflow(
            steps=steps,
            source_intent="TaskRuntime",
            correlation_id=correlation_id
        )
        workflow.metadata["created_by"] = "WorkflowBuilder"
        workflow.metadata["reasoning"] = step_data.reasoning
        
        return workflow
