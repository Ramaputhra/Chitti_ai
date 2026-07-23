from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

class SpeakerState(Enum):
    VERIFIED = "VERIFIED"
    UNKNOWN = "UNKNOWN"
    REJECTED = "REJECTED"

@dataclass
class VoiceProfile:
    owner_id: str
    created_at: str
    updated_at: str
    embeddings: List[List[float]] = field(default_factory=list)
    microphones_tested: List[str] = field(default_factory=list)
    confidence_threshold: float = 0.75
    model_version: str = "1.0"
    sample_count: int = 0
