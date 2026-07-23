import json
import time
from typing import Any, Dict, Optional

from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.logger import ILoggingService
from desktop.platform.shared.interfaces.event_bus import IEventBus, Event
from desktop.platform.shared.models.task import TaskContext, TaskState, TaskStepData, TaskObservation
from desktop.platform.shared.models.signals import SystemEvents
from desktop.runtimes.inference.router import InferenceRouter
from desktop.runtimes.inference.models import LLMRequest
from desktop.runtimes.inference.prompt_builder import PromptBuilder
from desktop.services.language.workflow_builder import WorkflowBuilder

class TaskOrchestrator:
    """
    Owns long-running, multi-step goals.
    Uses the Inference Runtime to generate TaskSteps and converts them to Workflows.
    """
    def __init__(
        self,
        logger: ILoggingService,
        event_bus: IEventBus,
        inference_router: InferenceRouter,
        prompt_builder: PromptBuilder,
        workflow_builder: WorkflowBuilder,
        template_registry: Any = None
    ) -> None:
        self.logger = logger
        self.event_bus = event_bus
        self.inference_router = inference_router
        self.prompt_builder = prompt_builder
        self.workflow_builder = workflow_builder
        self.template_registry = template_registry
        self._state = ServiceState.STOPPED
        
        # Track active tasks (task_id -> TaskContext)
        self.active_tasks: Dict[str, TaskContext] = {}

    @property
    def name(self) -> str:
        return "TaskOrchestrator"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self.event_bus.subscribe(SystemEvents.WORKFLOW_COMPLETED, self._on_workflow_completed)
        self.event_bus.subscribe(SystemEvents.TASK_STARTED, self._on_task_started)
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def _on_task_started(self, event: Event) -> None:
        context = event.payload.get("task_context")
        if context:
            self.start_task(context)

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def start_task(self, context: TaskContext) -> None:
        """Starts a scheduled long-running task."""
        self.active_tasks[context.task_id] = context
        self.logger.info(f"TaskOrchestrator started Task {context.task_id} [Goal: {context.goal}]")
        self._step_task(context)

    def _save_checkpoint(self, context: TaskContext) -> None:
        from desktop.platform.shared.models.task import TaskCheckpoint
        checkpoint = TaskCheckpoint(
            completed_steps=context.completed_steps.copy(),
            observations=context.observations.copy()
        )
        context.checkpoints.append(checkpoint)
        self.logger.info(f"Saved checkpoint {checkpoint.checkpoint_id} for Task {context.task_id}")

    def _step_task(self, context: TaskContext) -> None:
        """
        Execute the next iteration of the reasoning loop or template graph.
        """
        if context.state in [TaskState.COMPLETED, TaskState.FAILED]:
            self.logger.info(f"Task {context.task_id} is already {context.state.value}.")
            return
            
        try:
            if context.template_context:
                tc = context.template_context
                if not tc.cursor.current_node_uuid:
                    context.state = TaskState.COMPLETED
                    self.logger.info(f"Task {context.task_id} COMPLETED via Template.")
                    return
                    
                node = tc.compiled_nodes.get(tc.cursor.current_node_uuid)
                if not node:
                    raise ValueError(f"Template node {tc.cursor.current_node_uuid} not found.")
                    
                merged_params = tc.parameters.copy()
                merged_params.update(node.parameters)
                
                step_data = TaskStepData(
                    action_type=node.action,
                    parameters=merged_params,
                    reasoning=f"Executing template node: {node.id}"
                )
                context.current_state_summary = step_data.reasoning
                context.current_step = node.id
                context.current_workflow = node.action
                
                # Advance pointer for next iteration
                tc.cursor.visited.append(node.uuid)
                tc.cursor.last_completed = node.uuid
                tc.cursor.current_node_uuid = node.next
                # tc.cursor.pending could be managed later for DAGs
            else:
                # 1. Build Prompt (Task Planning/Continuation Prompt)
                prompt = self.prompt_builder.build_task_prompt(context)
                
                # 2. Invoke Inference
                request = LLMRequest(
                    prompt=prompt,
                    model_type="primary",
                    response_format="json"
                )
                response = self.inference_router.route(request)
                
                # 3. Parse LLM Output -> TaskStepData
                step_data = self._parse_llm_response(response.content)
                context.current_state_summary = step_data.reasoning
                context.current_step = step_data.action_type
                
                if step_data.action_type.lower() == "complete":
                    context.state = TaskState.COMPLETED
                    self.logger.info(f"Task {context.task_id} COMPLETED: {step_data.parameters.get('answer')}")
                    return
            
            # 4. Generate Workflow
            workflow = self.workflow_builder.build(step_data, context.correlation_id)
            context.active_workflow_id = workflow.workflow_id
            
            if context.state != TaskState.COMPLETED:
                context.state = TaskState.WAITING
            
            # 5. Dispatch Workflow
            self.event_bus.publish(
                Event(
                    SystemEvents.WORKFLOW_CREATED,
                    self.name,
                    {
                        "workflow": workflow,
                        "task_id": context.task_id
                    }
                )
            )
            
        except Exception as e:
            self.logger.error(f"Task {context.task_id} failed during reasoning step: {e}")
            context.retry_count = getattr(context, 'retry_count', 0) + 1
            max_retries = getattr(context, 'max_retries', 3)
            if context.retry_count >= max_retries:
                context.state = TaskState.FAILED
                self.logger.error(f"Task {context.task_id} FAILED permanently.")
            else:
                self.logger.info(f"Task {context.task_id} will retry ({context.retry_count}/{max_retries})")
                self._step_task(context)

    def _on_workflow_completed(self, event: Event) -> None:
        """
        Intercepts completed workflows. If the workflow belongs to an active task,
        record the observation and continue the loop.
        """
        workflow_id = event.payload.get("workflow_id")
        result_payload = event.payload.get("result", {})
        
        # Find the task awaiting this workflow
        for task_id, context in self.active_tasks.items():
            if context.active_workflow_id == workflow_id and context.state == TaskState.WAITING:
                self.logger.info(f"Task {task_id} received result for Workflow {workflow_id}")
                
                # 1. Record Observation
                success = result_payload.get("success", False)
                output = result_payload.get("output", "")
                error = result_payload.get("error", "")
                obs = TaskObservation(
                    step_id=workflow_id,
                    result=output if success else error,
                    success=success
                )
                context.observations.append(obs)
                context.active_workflow_id = None
                context.state = TaskState.RUNNING
                
                # 2. Continue the loop
                self._step_task(context)
                break

    def _parse_llm_response(self, content: str) -> TaskStepData:
        """Extracts JSON from LLM response and constructs TaskStepData."""
        # Simple extraction logic
        try:
            # Try to find JSON block if wrapped in markdown
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
                
            data = json.loads(json_str)
            return TaskStepData(
                action_type=data.get("action", "invoke"),
                parameters=data.get("parameters", {}),
                reasoning=data.get("reasoning", "")
            )
        except Exception as e:
            self.logger.error(f"Failed to parse LLM response into TaskStepData: {e}\nContent: {content}")
            raise Exception("Invalid LLM format for Task Step")
