import queue
from typing import Dict, Optional, Tuple

from desktop.platform.shared.models.workflow import Workflow, WorkflowPriority, WorkflowState

class WorkflowScheduler:
    """
    Manages the Workflow Queue.
    Supports Priority-based FIFO queueing.
    Provides API for enqueueing, pausing, and cancelling without executing.
    """
    def __init__(self) -> None:
        # PriorityQueue uses (priority_value, timestamp, workflow) for deterministic ordering
        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        self._workflows: Dict[str, Workflow] = {}
        self._paused: Dict[str, bool] = {}

    def enqueue(self, workflow: Workflow) -> None:
        """Adds a workflow to the queue based on its priority."""
        self._workflows[workflow.workflow_id] = workflow
        # priority enum value (1=CRITICAL, 5=BACKGROUND), then timestamp for FIFO within priority
        item = (workflow.priority.value, workflow.timestamp, workflow)
        self._queue.put(item)
        workflow.state = WorkflowState.QUEUED

    def cancel(self, workflow_id: str) -> None:
        """Mark workflow as cancelled. It will be skipped if dequeued."""
        if workflow_id in self._workflows:
            self._workflows[workflow_id].state = WorkflowState.CANCELLED

    def pause(self, workflow_id: str) -> None:
        """Pause a workflow. It will not be yielded by next_ready."""
        if workflow_id in self._workflows:
            self._paused[workflow_id] = True

    def resume(self, workflow_id: str) -> None:
        """Resume a paused workflow."""
        if workflow_id in self._paused:
            self._paused[workflow_id] = False

    def next_ready(self) -> Optional[Workflow]:
        """
        Retrieves the next highest-priority workflow that is not cancelled or paused.
        This allows the Kernel to pull work sequentially (or concurrently if using thread pools).
        """
        while not self._queue.empty():
            try:
                priority, ts, workflow = self._queue.get_nowait()
                
                # Skip cancelled workflows
                if workflow.state == WorkflowState.CANCELLED:
                    continue
                    
                # Skip paused workflows (in a real system, we might re-queue them or store elsewhere)
                if self._paused.get(workflow.workflow_id, False):
                    continue
                    
                return workflow
                
            except queue.Empty:
                break
                
        return None
