from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class IdentityEvent:
    event_type: str
    timestamp: float
    payload: Dict[str, Any] = field(default_factory=dict)

class IdentityLoaded(IdentityEvent):
    def __init__(self, timestamp: float, character_id: str, profile_version: str):
        super().__init__("IdentityLoaded", timestamp, {"character_id": character_id, "profile_version": profile_version})

class IdentityReloaded(IdentityEvent):
    def __init__(self, timestamp: float, character_id: str):
        super().__init__("IdentityReloaded", timestamp, {"character_id": character_id})

class IdentityProfileChanged(IdentityEvent):
    def __init__(self, timestamp: float, character_id: str, updated_fields: Dict[str, Any]):
        super().__init__("IdentityProfileChanged", timestamp, {"character_id": character_id, "updated_fields": updated_fields})

class IdentityValidationFailed(IdentityEvent):
    def __init__(self, timestamp: float, errors: list):
        super().__init__("IdentityValidationFailed", timestamp, {"errors": errors})
