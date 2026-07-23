import time
from dataclasses import dataclass, field
from typing import List

from desktop.platform.shared.models.vision_artifact import Observation


@dataclass
class PerceptionModel:
    """
    The unified base model for all perception domains (Screen, Scene, Robot, Audio).
    This enforces Engineering Rule 14 across all runtimes.
    """
    source: str = ""
    timestamp: float = field(default_factory=time.time)
    coordinate_frame: str = ""
    confidence: float = 0.0
    observations: List[Observation] = field(default_factory=list)
    summary: str = ""
