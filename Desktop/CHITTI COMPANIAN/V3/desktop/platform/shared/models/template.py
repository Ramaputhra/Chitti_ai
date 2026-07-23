import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class TaskTemplateDescriptor:
    """Metadata describing a reusable task template (Rule 71). Cached by TemplateRegistry."""
    id: str
    version: str
    schema_version: int
    goal: str
    summary: str
    category: str
    author: str
    required_inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    permissions: List[str]
    estimated_duration: str
    tags: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class TemplateNode:
    """A node in the declarative template graph (Forward-compatible for DAGs)."""
    id: str
    uuid: str
    action: Optional[str] = None
    type: str = "capability" # "capability" or "approval"
    message: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    next: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    retry_policy: Optional[str] = None

@dataclass(frozen=True)
class CompiledTemplate:
    """A validated, executable template with its node definitions."""
    descriptor: TaskTemplateDescriptor
    nodes: Dict[str, TemplateNode]
    entry_node_id: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    compiled_at: float = field(default_factory=time.time)

@dataclass
class ExecutionCursor:
    """Tracks execution progress within a Template (Rule 73)."""
    current_node_uuid: Optional[str] = None
    visited: List[str] = field(default_factory=list)
    pending: List[str] = field(default_factory=list)
    last_completed: Optional[str] = None
    started_at: float = field(default_factory=time.time)

@dataclass
class TemplateContext:
    """
    Context for an instantiated template during execution (Rule 72).
    Keeps template state separate from orchestration state.
    """
    template_id: str
    version: str
    parameters: Dict[str, Any]
    compiled_nodes: Dict[str, TemplateNode]
    cursor: ExecutionCursor = field(default_factory=ExecutionCursor)
