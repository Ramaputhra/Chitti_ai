import time
from typing import Optional
from datetime import datetime

class CancellationContext:
    def __init__(self, workflow_id: str, parent_workflow_id: Optional[str] = None, timeout: Optional[float] = None):
        self.workflow_id = workflow_id
        self.parent_workflow_id = parent_workflow_id
        self.created_at = datetime.utcnow()
        self.cancelled_by: Optional[str] = None
        self._timeout = timeout
        self._cancellation_requested = False
        self._cancel_reason = None
        self._deadline = time.time() + timeout if timeout else None

    @property
    def cancellation_requested(self) -> bool:
        if self._cancellation_requested:
            return True
        if self._deadline and time.time() > self._deadline:
            self._cancellation_requested = True
            self._cancel_reason = "Timeout exceeded"
            self.cancelled_by = "Scheduler"
            return True
        return False

    @property
    def cancel_reason(self) -> Optional[str]:
        return self._cancel_reason

    def request_cancellation(self, reason: str, cancelled_by: str = "System"):
        self._cancellation_requested = True
        self._cancel_reason = reason
        self.cancelled_by = cancelled_by

    def check(self):
        if self.cancellation_requested:
            raise Exception(f"Operation Cancelled by {self.cancelled_by}: {self.cancel_reason}")
