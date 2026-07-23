import enum
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime

class InsightCategory(enum.Enum):
    ANALYTICS = "analytics"
    PREDICTION = "prediction"
    MEMORY = "memory"
    BEHAVIOR = "behavior"

@dataclass
class InsightSource:
    name: str
    confidence_contribution: float
    description: Optional[str] = None

@dataclass
class Insight:
    """
    A foundational platform concept representing a deterministic or derived understanding.
    Used by Analytics, Prediction, Memory, and Presentation runtimes.
    """
    insight_id: str
    title: str
    description: str
    category: InsightCategory
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    sources: List[InsightSource] = field(default_factory=list)
