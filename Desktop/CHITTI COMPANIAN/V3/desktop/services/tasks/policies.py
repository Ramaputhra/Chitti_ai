from dataclasses import dataclass, field
from typing import List

@dataclass
class TaskPolicy:
    """
    Defines execution constraints and rules for a Task.
    """
    max_runtime_sec: int = 900  # Default 15 minutes
    retry_allowed: bool = True
    max_retries: int = 3
    retry_backoff_sec: int = 5
    permission_requirements: List[str] = field(default_factory=list)
    interruptible: bool = True
    background_execution: bool = True
    concurrency_limit: int = 1
