import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Provenance:
    provider: str
    session_id: str
    conversation_id: Optional[str] = None
    artifact_id: Optional[str] = None
    prompt_id: Optional[str] = None
    model: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class EntityEvidence:
    artifact_id: str
    provider: str
    confidence: float
    reason: str
