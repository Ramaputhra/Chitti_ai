import json
import os
from datetime import datetime
from typing import Any, Dict

from desktop.platform.shared.models.workflow import WorkflowState

class PersistenceManager:
    """
    Event Sourcing Lite.
    Records an append-only event history of workflows to local disk.
    This enables full replayability and debugging months later.
    """
    def __init__(self, log_dir: str = ".data/workflows") -> None:
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def _get_file_path(self, workflow_id: str) -> str:
        return os.path.join(self.log_dir, f"workflow_{workflow_id}.events")

    def record_event(self, workflow_id: str, state: WorkflowState, metadata: Dict[str, Any] = None) -> None:
        """
        Append a state transition or lifecycle event to the workflow's log file.
        """
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "state": state.value,
            "metadata": metadata or {}
        }
        
        path = self._get_file_path(workflow_id)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")

    def record_step_result(self, workflow_id: str, step_id: str, result: Any) -> None:
        """
        Records the ExecutionResult of a specific step.
        """
        # Convert dataclass/result to dict if necessary, depending on how it's passed
        # For prototype simplicity, assuming result has a __dict__ or we manually map it
        result_dict = result.__dict__ if hasattr(result, "__dict__") else str(result)
        
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "StepResult",
            "step_id": step_id,
            "result": result_dict
        }
        
        path = self._get_file_path(workflow_id)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
