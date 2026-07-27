from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from desktop.models.conversation import ConversationArtifact

@dataclass
class CapabilityAction:
    """Represents an action that a capability can perform."""
    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None

@dataclass
class CapabilityResult:
    """
    Legacy result format for backward compatibility.
    Use CanonicalCapabilityOutput for new capabilities.
    """
    title: str
    summary: str
    status: str = "SUCCESS"
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0

@dataclass
class ExecutionResult:
    success: bool
    payload: Dict[str, Any]
    error_message: Optional[str] = None

@dataclass
class VerificationResult:
    verified: bool
    evidence_ids: List[str]
    verification_strategy: str

@dataclass
class PresentationDescriptor:
    experience_id: str
    recipe_id: str
    layout_data: Dict[str, Any]

@dataclass
class MemoryCandidate:
    activity_type: str
    workspace_hint: str
    related_entities: List[str]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CanonicalCapabilityOutput:
    """
    The rigid output contract for all V1 production capabilities.
    Capabilities MUST yield this aggregate object to ensure full traversal of the platform spine.
    """
    execution_result: ExecutionResult
    verification_result: VerificationResult
    conversation_artifact: ConversationArtifact
    presentation_descriptor: PresentationDescriptor
    memory_candidate: MemoryCandidate
