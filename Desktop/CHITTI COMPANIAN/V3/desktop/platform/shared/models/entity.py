from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


from desktop.platform.shared.models.entity_id import EntityResolutionStatus

@dataclass
class BaseEntity:
    """Base class for canonical extracted entities."""
    original_text: str
    confidence: float
    source: str = "speech"
    resolution: Optional[EntityResolutionStatus] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersonEntity(BaseEntity):
    """Normalized person identity."""
    display_name: str = ""
    contact_id: Optional[str] = None


@dataclass
class TimeEntity(BaseEntity):
    """Normalized timestamp."""
    timestamp: str = ""  # ISO-8601 string
    timezone: str = "UTC"


@dataclass
class LocationEntity(BaseEntity):
    """Normalized location coordinates/places."""
    display_name: str = ""
    coordinates: Optional[tuple[float, float]] = None


@dataclass
class ResolvedPerson(PersonEntity):
    """An identity-resolved person with a known entity ID in memory."""
    entity_id: str = ""
    aliases: List[str] = field(default_factory=list)
    resolution_confidence: float = 0.0


@dataclass
class ResolvedLocation(LocationEntity):
    """An identity-resolved location with a known entity ID in memory."""
    entity_id: str = ""
    saved_name: str = ""
    resolution_confidence: float = 0.0
