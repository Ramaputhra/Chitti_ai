from dataclasses import dataclass
from desktop.platform.shared.models.artifact import Artifact


@dataclass
class PerceptionArtifact(Artifact):
    """
    The unified base class for all multi-modal perception artifacts 
    (Vision, Screen, Audio, Touch, Sensor).
    """
    source: str = ""
    timestamp: float = 0.0
    coordinate_frame: str = ""
    confidence: float = 0.0
    observation_id: str = ""
    session_id: str = ""
