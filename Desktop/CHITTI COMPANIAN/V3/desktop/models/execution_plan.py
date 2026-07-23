from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ExecutionDelta:
    """Generalized model for tracking execution verification."""
    expected: List[str] = field(default_factory=list)
    observed: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

@dataclass
class ExecutionPolicy:
    """Declarative execution constraints and behaviors for a single plan node."""
    retry_strategy: str = "none"
    timeout_ms: Optional[int] = None
    continue_on_failure: bool = False
    verification_required: bool = True
    rollback_policy: str = "none"
    parallel_eligible: bool = False
    priority: int = 1

@dataclass
class ExecutionPlanNode:
    """Represents a single executable capability node within an ExecutionPlan."""
    node_id: str
    capability_id: str
    tool_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # IDs of nodes that must complete first
    policy: Optional[ExecutionPolicy] = None
    conditional_execution: Optional[Any] = None

@dataclass
class ExecutionPlan:
    """
    Abstract representation of the dependency graph produced by PlannerRuntime.
    Provides the abstraction boundary for Dependency ordering, Parallel execution, Retry policies,
    Cancellation, Pause / Resume, and Conditional execution.
    """
    plan_id: str
    nodes: List[ExecutionPlanNode] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)
