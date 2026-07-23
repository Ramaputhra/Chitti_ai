from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from desktop.platform.shared.models.observation import Observation


class TemporalObservationStatus(Enum):
    NEW = "new"
    ACTIVE = "active"
    LOST = "lost"
    EXPIRED = "expired"


@dataclass
class TemporalObservation:
    """
    Wraps an Observation to add temporal continuity across multiple frames.
    Allows downstream components to rank based on time, and build a World Model.
    """
    observation: Observation
    first_seen: float
    last_seen: float
    occurrence_count: int
    status: TemporalObservationStatus
    last_transition: float
    revision: int = 1
    active_duration: float = 0.0
    inactive_duration: float = 0.0

    def age(self, current_time: float) -> float:
        return current_time - self.first_seen

    @property
    def duration(self) -> float:
        return self.last_seen - self.first_seen

    def to_dict(self, current_time: float) -> Dict[str, Any]:
        return {
            "observation": self.observation.__dict__, # Simplification for context passing
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "duration": self.duration,
            "age": self.age(current_time),
            "active_duration": self.active_duration,
            "inactive_duration": self.inactive_duration,
            "occurrence_count": self.occurrence_count,
            "status": self.status.value,
            "last_transition": self.last_transition,
            "revision": self.revision
        }
