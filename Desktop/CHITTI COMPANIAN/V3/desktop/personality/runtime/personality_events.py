from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class PersonalityEvent:
    event_type: str
    timestamp: float
    payload: Dict[str, Any] = field(default_factory=dict)

class ProfileLoaded(PersonalityEvent):
    def __init__(self, timestamp: float, profile_name: str):
        super().__init__("ProfileLoaded", timestamp, {"profile_name": profile_name})

class ProfileChanged(PersonalityEvent):
    def __init__(self, timestamp: float, profile_name: str, changes: Dict[str, float]):
        super().__init__("ProfileChanged", timestamp, {"profile_name": profile_name, "changes": changes})

class PresetApplied(PersonalityEvent):
    def __init__(self, timestamp: float, preset_name: str):
        super().__init__("PresetApplied", timestamp, {"preset_name": preset_name})

class SettingsUpdated(PersonalityEvent):
    def __init__(self, timestamp: float, updated_fields: Dict[str, Any]):
        super().__init__("SettingsUpdated", timestamp, {"updated_fields": updated_fields})
