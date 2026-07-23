from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass(frozen=True)
class InferenceTelemetryRecord:
    correlation_id: str
    interaction_id: str
    plan_id: Optional[str]
    
    prompt_version: str
    prompt_hash: str
    
    provider_name: str
    model_name: str
    
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    
    validation_outcome: str # e.g. "PASS", "CLAMPED", "FAIL"
    raw_confidence: float
    planner_outcome: str # e.g. "GreetingIntent", "ClarificationIntent"

@dataclass
class ContextSelectionTrace:
    correlation_id: str
    selector: str
    policy: str
    selected_items: list[str]
    discarded_items: list[str]
    budget_used: int
    selection_reasons: list[str]

@dataclass
class ClarificationTrace:
    correlation_id: str
    workflow_id: str
    pending_intent_id: str
    question: str
    target_parameter: str
    response: str
    resolution_time: float
    resume_result: str

@dataclass
class RecommendationTrace:
    workflow_id: str
    user_request: str
    candidate_capabilities: list[str]
    accepted_capability: str
    rejected_capabilities: list[str]
    rejection_reasons: dict
    parameter_confidence: float
    validation_latency_ms: float
    clarification_triggered: bool
    planner_decision: str

from enum import Enum

class ReplayMode(Enum):
    OFF = "OFF"
    METADATA_ONLY = "METADATA_ONLY"
    FULL = "FULL"

@dataclass(frozen=True)
class PromptReplayRecord:
    timestamp: str
    prompt_hash: str
    provider_name: str
    model_name: str
    
    # Metadata
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    confidence: float
    
    # Content (only populated if ReplayMode is FULL)
    request_payload: Optional[str]
    response_payload: Optional[str]
    
    validation_outcome: str
    planner_outcome: str

@dataclass
class ExecutionTelemetry:
    """Strongly typed telemetry object for capability execution."""
    capability: str
    duration_ms: int
    status: str
    verification: bool
    target: Optional[str] = None
