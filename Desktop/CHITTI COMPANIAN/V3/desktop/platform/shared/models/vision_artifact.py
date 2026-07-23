from dataclasses import dataclass, field
from typing import Any, Dict, List

from desktop.platform.shared.models.perception_artifact import PerceptionArtifact


@dataclass
class Observation:
    """
    Standard observation contract representing what a Vision Provider 'sees'.
    """
    label: str
    confidence: float
    location_box: List[int]  # Unified vision coordinate [x1, y1, x2, y2]
    tracking_id: str = ""
    timestamp: float = 0.0


@dataclass
class VisionArtifact(PerceptionArtifact):
    """Base class for all visual artifacts. Ensures Knowledge Runtime can instantly digest them."""
    source_image_id: str = ""


@dataclass
class ImageArtifact(VisionArtifact):
    resolution: str = ""
    color_space: str = ""


@dataclass
class OCRArtifact(VisionArtifact):
    text: str = ""
    language: str = ""
    confidence: float = 0.0
    bounding_boxes: List[List[int]] = field(default_factory=list)


@dataclass
class FaceArtifact(VisionArtifact):
    observations: List[Observation] = field(default_factory=list)


@dataclass
class ObjectArtifact(VisionArtifact):
    observations: List[Observation] = field(default_factory=list)


@dataclass
class SceneArtifact(VisionArtifact):
    """Produced by the SceneInterpreter. Contains semantic meaning rather than raw labels."""
    description: str = ""
