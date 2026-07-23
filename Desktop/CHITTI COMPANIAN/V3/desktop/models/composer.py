from enum import Enum
from typing import List, Dict, Any
from dataclasses import dataclass, field
from desktop.models.service_registry import ServiceDescriptor

class CompositionPolicy(Enum):
    STRICT = "STRICT"
    OFFLINE_FIRST = "OFFLINE_FIRST"
    FASTEST = "FASTEST"
    LOWEST_COST = "LOWEST_COST"
    HIGHEST_ACCURACY = "HIGHEST_ACCURACY"
    LOCAL_ONLY = "LOCAL_ONLY"

@dataclass
class WorkflowNode:
    """
    Represents a single executable step bound to a capability.
    Rule 301: Node is ignorant of its successors in code.
    """
    node_id: str
    service_id: str
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list) # node_ids of predecessors

@dataclass
class ServiceChain:
    """
    A linear sequence of capabilities chosen deterministically by the Composer.
    """
    input_type: str
    output_type: str
    steps: List[ServiceDescriptor] = field(default_factory=list)
    confidence: float = 1.0
    estimated_latency_ms: int = 0
    estimated_cost: int = 0

@dataclass
class WorkflowBlueprint:
    """
    Rule 302: Declarative Workflow.
    Rule 303: Planner receives this already-composed DAG.
    """
    blueprint_id: str
    intent: str
    nodes: Dict[str, WorkflowNode] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = False
    validation_trace: List[str] = field(default_factory=list)
