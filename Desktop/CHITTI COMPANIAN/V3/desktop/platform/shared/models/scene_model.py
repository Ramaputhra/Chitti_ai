import time
from dataclasses import dataclass, field
from typing import List, Any

from desktop.platform.shared.models.perception_model import PerceptionModel
from desktop.platform.shared.models.entity import PersonEntity, LocationEntity


@dataclass
class SceneModel(PerceptionModel):
    """
    The unified domain model built by the Vision Runtime before any VisionArtifacts
    are published. Models the physical environment.
    """
    frame_id: str
    people: List[PersonEntity] = field(default_factory=list)
    objects: List[Any] = field(default_factory=list)
    faces: List[Any] = field(default_factory=list)
    gestures: List[str] = field(default_factory=list)
    lighting: str = "normal"
    motion: str = "none"
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
