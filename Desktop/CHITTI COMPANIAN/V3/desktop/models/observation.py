from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class Observation:
    """
    Canonical, read-only representation of deterministic desktop state.
    Produced by Observation Sources. No interpretation logic allowed.
    """
    observation_id: str
    correlation_id: str
    session_id: str
    observation_type: str
    timestamp: datetime
    source: str
    payload: Dict[str, Any]
    confidence: float = 1.0
    source_reliability: float = 1.0
