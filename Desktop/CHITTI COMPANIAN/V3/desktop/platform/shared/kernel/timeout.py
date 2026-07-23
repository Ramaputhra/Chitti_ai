import threading
from typing import Dict
from desktop.platform.shared.kernel.cancellation import CancellationManager

class TimeoutManager:
    """
    Handles step/workflow timeouts and cancellation propagation.
    Instead of hardcoded timeout loops inside the executor, the TimeoutManager
    schedules timer callbacks that interact with the CancellationManager.
    """
    def __init__(self, cancellation_manager: CancellationManager) -> None:
        self._cancellation_manager = cancellation_manager
        # Maps workflow_id -> step_id -> Timer
        self._timers: Dict[str, Dict[str, threading.Timer]] = {}

    def schedule_timeout(self, workflow_id: str, step_id: str, timeout_ms: int) -> None:
        """
        Schedules a cancellation request after the specified timeout_ms.
        """
        if workflow_id not in self._timers:
            self._timers[workflow_id] = {}

        # Convert ms to seconds for threading.Timer
        timeout_sec = timeout_ms / 1000.0

        def on_timeout():
            self._cancellation_manager.request_cancellation(
                workflow_id=workflow_id,
                reason=f"Step {step_id} exceeded timeout of {timeout_ms}ms",
                requested_by="TimeoutManager"
            )

        timer = threading.Timer(timeout_sec, on_timeout)
        timer.daemon = True
        self._timers[workflow_id][step_id] = timer
        timer.start()

    def cancel_timeout(self, workflow_id: str, step_id: str) -> None:
        """
        Cancels the scheduled timeout if the step completes successfully before expiration.
        """
        workflow_timers = self._timers.get(workflow_id, {})
        timer = workflow_timers.pop(step_id, None)
        if timer:
            timer.cancel()

    def cleanup_workflow(self, workflow_id: str) -> None:
        """
        Ensures no dangling timers remain for a workflow.
        """
        workflow_timers = self._timers.pop(workflow_id, {})
        for timer in workflow_timers.values():
            timer.cancel()
