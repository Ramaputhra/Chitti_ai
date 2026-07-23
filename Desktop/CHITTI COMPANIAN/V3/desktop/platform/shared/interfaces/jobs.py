from enum import Enum
from typing import Any, Dict, List, Protocol


class JobStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IJobStep(Protocol):
    """
    A single link in a workflow chain. Context is passed sequentially.
    """
    def execute(self, context: Dict[str, Any]) -> None:
        ...


class JobDefinition:
    def __init__(self, name: str, steps: List[IJobStep]) -> None:
        self.name = name
        self.steps = steps


class IJobManager(Protocol):
    """
    Manages long-running sequential workflows asynchronously.
    Example: Download PDF -> Summarize -> Translate -> Save -> Notify
    """
    def submit(self, job: JobDefinition, initial_context: Dict[str, Any] | None = None) -> str:
        """Submits a job for execution and returns the Job ID."""
        ...

    def status(self, job_id: str) -> JobStatus:
        """Queries the status of a submitted job."""
        ...
