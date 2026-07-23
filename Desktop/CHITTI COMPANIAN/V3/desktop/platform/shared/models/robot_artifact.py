from dataclasses import dataclass

from desktop.platform.shared.models.perception_artifact import PerceptionArtifact


@dataclass
class RobotArtifact(PerceptionArtifact):
    """Base class for artifacts originating from the Robot Runtime (Sensors)."""
    pass


@dataclass
class TouchArtifact(RobotArtifact):
    zone: str = ""
    action: str = ""


@dataclass
class SensorArtifact(RobotArtifact):
    sensor_type: str = ""
    semantic_state: str = ""  # e.g., "Fallen", "Approaching"


@dataclass
class TelemetryArtifact(RobotArtifact):
    category: str = ""
    status: str = ""
