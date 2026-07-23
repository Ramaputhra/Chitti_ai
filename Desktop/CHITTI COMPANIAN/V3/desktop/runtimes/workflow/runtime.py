import asyncio
import logging
from typing import Any, Dict
from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event
from desktop.platform.shared.models.workflow import Workflow
from desktop.runtimes.workflow.executor import WorkflowExecutor
from desktop.runtimes.capability.runtime import CapabilityRuntime

logger = logging.getLogger(__name__)

class WorkflowRuntime:
    """
    The orchestrator of workflows. Subscribes to Planner output (WORKFLOW_CREATED)
    and manages individual WorkflowExecutors.
    """
    def __init__(self, event_bus: Any, capability_runtime: CapabilityRuntime):
        self.event_bus = event_bus
        self.capability_runtime = capability_runtime
        self.executors: Dict[str, WorkflowExecutor] = {}

    def start(self):
        """Subscribe to events and initialize."""
        if hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe(SystemEvents.WORKFLOW_CREATED, self._handle_workflow_created)
            self.event_bus.subscribe(SystemEvents.APP_STOPPING, self._handle_app_stopping)
            logger.info("WorkflowRuntime initialized and subscribed to WORKFLOW_CREATED.")

    def stop(self):
        """Cleanup and shutdown."""
        self._handle_app_stopping(None)

    async def _handle_workflow_created(self, event: Event):
        """Spawns an executor for a newly created workflow."""
        workflow: Workflow = event.payload.get("workflow")
        if not workflow:
            logger.warning("Received WORKFLOW_CREATED event without workflow payload.")
            return
            
        executor = WorkflowExecutor(workflow, self.event_bus, self.capability_runtime)
        self.executors[workflow.workflow_id] = executor
        
        # Fire and forget execution; the executor manages its own state and event publishing
        asyncio.create_task(self._run_executor_and_cleanup(executor, workflow.workflow_id))

    async def _run_executor_and_cleanup(self, executor: WorkflowExecutor, workflow_id: str):
        try:
            await executor.execute()
        except Exception as e:
            logger.exception(f"Unhandled exception executing workflow {workflow_id}: {e}")
        finally:
            self.executors.pop(workflow_id, None)

    async def _handle_app_stopping(self, event: Event):
        """Cooperatively cancels all running workflows during shutdown."""
        logger.info("WorkflowRuntime shutting down. Cancelling all active workflows.")
        for executor in self.executors.values():
            executor.cancel()
