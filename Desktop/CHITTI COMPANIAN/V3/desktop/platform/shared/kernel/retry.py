import time
from typing import Dict
from desktop.platform.shared.models.workflow import ExecutionPolicy

class RetryManager:
    """
    Manages interactive backoff (100ms -> 300ms -> 800ms) for idempotent steps.
    """
    BACKOFF_SCHEDULE = [0.1, 0.3, 0.8]  # In seconds

    def __init__(self) -> None:
        # Maps workflow_id -> step_id -> retry_count
        self._retry_counts: Dict[str, Dict[str, int]] = {}

    def get_retry_count(self, workflow_id: str, step_id: str) -> int:
        return self._retry_counts.get(workflow_id, {}).get(step_id, 0)

    def should_retry(self, workflow_id: str, step_id: str, policy: ExecutionPolicy) -> bool:
        """
        Determines if a step should be retried based on its ExecutionPolicy.
        """
        if not policy.retryable or not policy.idempotent:
            return False
            
        current_retries = self.get_retry_count(workflow_id, step_id)
        return current_retries < policy.max_retries

    def record_failure_and_wait(self, workflow_id: str, step_id: str) -> None:
        """
        Increments the retry counter and applies the interactive backoff sleep.
        """
        if workflow_id not in self._retry_counts:
            self._retry_counts[workflow_id] = {}
        
        current_retries = self._retry_counts[workflow_id].get(step_id, 0)
        
        # Determine backoff duration based on schedule, capping at the last element
        sleep_idx = min(current_retries, len(self.BACKOFF_SCHEDULE) - 1)
        sleep_sec = self.BACKOFF_SCHEDULE[sleep_idx]
        
        self._retry_counts[workflow_id][step_id] = current_retries + 1
        
        # In a fully async system this would be asyncio.sleep
        # For the prototype phase, we block
        time.sleep(sleep_sec)

    def cleanup_workflow(self, workflow_id: str) -> None:
        self._retry_counts.pop(workflow_id, None)
