"""
PlanningContext and PlanningResult — the data contracts between the
Intent layer and the Cognitive Pipeline.

The Planner builds a PlanningContext from all available system state,
passes it to the DecisionEngine, and receives a PlanningResult back.
The Workflow embedded in the PlanningResult is then dispatched for execution.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from desktop.platform.shared.models.workflow import Workflow


@dataclass
class MemoryContext:
    active_projects: List[str] = field(default_factory=list)
    recent_entities: List[str] = field(default_factory=list)
    relevant_facts: List[str] = field(default_factory=list)


@dataclass
class DeviceContext:
    battery_level: float = 1.0
    is_charging: bool = False
    network_status: str = "online"


@dataclass
class SensorContext:
    distance_cm: float = 0.0
    ambient_light: float = 1.0
    face_detected: bool = False
    person_nearby: bool = False
    motion_detected: bool = False


@dataclass
class PlanningContext:
    """
    A snapshot of all system state at the moment planning is requested.
    The Planner API never changes as data sources become real.
    """
    user_input: str
    intent_type: str
    intent_confidence: float = 1.0
    conversation_state: Dict[str, Any] = field(default_factory=dict)
    emotion: str = "Neutral"
    active_goal: Optional[str] = None
    memory_context: MemoryContext = field(default_factory=MemoryContext)
    device_context: DeviceContext = field(default_factory=DeviceContext)
    sensor_context: SensorContext = field(default_factory=SensorContext)
    timestamp: float = field(default_factory=time.time)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Decision:
    """
    Technology-agnostic output of the DecisionEngine.
    Describes *what* needs to happen, not *how* it gets executed.
    """
    route: str                           # "capability", "memory", "clarification", "reasoning", "task"
    target: Optional[str] = None         # capability_id, memory_query, clarification_question
    confidence: float = 1.0
    requires_confirmation: bool = False
    memory_action: Optional[str] = None  # "store", "retrieve", "none"
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    decision_path: List[str] = field(default_factory=list)


@dataclass
class PlanningResult:
    """
    The final output of the ActionPlanner.
    Contains the immutable Workflow for the Executor and full diagnostic trace.
    """
    success: bool
    confidence: float
    workflow: Optional[Workflow]
    decision: Optional[Decision] = None
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
