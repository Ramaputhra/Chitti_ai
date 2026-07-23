from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class DailyHealth(Enum):
    HEALTHY = "Healthy"
    BUSY = "Busy"
    NEEDS_ATTENTION = "Needs Attention"
    CRITICAL = "Critical"

@dataclass
class BriefingMemoryModel:
    """Remembers what has already been briefed to avoid repetition."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    daily_health: DailyHealth = DailyHealth.HEALTHY
    briefed_items: List[str] = field(default_factory=list)
    dismissed_items: List[str] = field(default_factory=list)
    completed_items: List[str] = field(default_factory=list)
    deferred_items: List[str] = field(default_factory=list)
