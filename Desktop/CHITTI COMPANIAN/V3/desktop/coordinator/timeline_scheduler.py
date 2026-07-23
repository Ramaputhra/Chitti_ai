import time
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

@dataclass
class TimelineItem:
    item_id: str
    timeline_type: str   # "Speech", "Character", "Widget", "Presentation", "Notification", "Execution"
    scheduled_time: float
    duration_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class TimelineScheduler:
    """
    S36E: Single Source of Timing Truth merging Speech, Character, Widget, Presentation, Notification, and Execution Timelines.
    """
    def __init__(self):
        self._unified_timeline: List[TimelineItem] = []

    def schedule_timeline(self, items: List[TimelineItem]):
        self._unified_timeline.extend(items)
        self._unified_timeline.sort(key=lambda x: x.scheduled_time)
        logger.info(f"[TimelineScheduler] Merged {len(items)} items into Unified Timeline (Total: {len(self._unified_timeline)}).")

    def get_unified_timeline(self) -> List[TimelineItem]:
        return list(self._unified_timeline)

    def clear(self):
        self._unified_timeline.clear()
