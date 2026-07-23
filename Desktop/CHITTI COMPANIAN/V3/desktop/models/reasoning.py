from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

class ReasoningStrategy(Enum):
    DIRECT = "DIRECT"
    DETERMINISTIC = "DETERMINISTIC"
    KNOWLEDGE = "KNOWLEDGE"
    HYBRID = "HYBRID"
    AI_ASSISTED = "AI_ASSISTED"
    PRESENTATION = "PRESENTATION"
    EXECUTION = "EXECUTION"

class ReasoningMode(Enum):
    NONE = "NONE"
    LOCAL_RULES = "LOCAL_RULES"
    LOCAL_MODEL = "LOCAL_MODEL"
    REMOTE_MODEL = "REMOTE_MODEL"
    HYBRID = "HYBRID"

@dataclass
class ReasoningCapabilityProfile:
    """Future-proofs offline operation requirements."""
    reasoning_mode: ReasoningMode = ReasoningMode.LOCAL_RULES
    required_provider: Optional[str] = None

@dataclass
class DecisionTrace:
    """
    Rule 295: Every decision must be traceable.
    """
    step: str
    rule: str
    result: Any
    confidence: float
    timestamp: float

@dataclass
class ReasoningPlan:
    """
    Rule 293: Planner orchestrates this plan; it does not reinterpret it.
    """
    strategy: ReasoningStrategy = ReasoningStrategy.DIRECT
    capability_profile: ReasoningCapabilityProfile = field(default_factory=ReasoningCapabilityProfile)
    
    requires_execution: bool = False
    requires_retrieval: bool = False
    requires_ai: bool = False
    requires_presentation: bool = False
    requires_behavior: bool = False
    requires_confirmation: bool = False
    requires_authentication: bool = False
    requires_memory: bool = False
    requires_web: bool = False
    requires_plugin: bool = False
    requires_document_parser: bool = False
    
    preferred_services: List[str] = field(default_factory=list)
    confidence: float = 1.0
    reasoning_trace: List[DecisionTrace] = field(default_factory=list)
    decision_time_ms: int = 0
