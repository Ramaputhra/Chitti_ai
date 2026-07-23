import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from desktop.runtimes.workflow.cancellation import CancellationToken
from desktop.runtimes.workflow.models import StepExecutionRecord

@dataclass
class WorkflowContext:
    """
    Holds orchestration state during workflow execution.
    Owned exclusively by the Workflow Runtime.
    """
    workflow_id: str
    execution_id: str
    cancellation_token: CancellationToken = field(default_factory=CancellationToken)
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Rule 25: Idempotency tracked via exact execution records
    execution_records: List[StepExecutionRecord] = field(default_factory=list)
    completed_steps: List[str] = field(default_factory=list)
    
    started_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    telemetry: Dict[str, Any] = field(default_factory=dict)

    def add_record(self, record: StepExecutionRecord):
        self.execution_records.append(record)
        
    def get_latest_record(self, step_id: str) -> Optional[StepExecutionRecord]:
        for record in reversed(self.execution_records):
            if record.step_id == step_id:
                return record
        return None
