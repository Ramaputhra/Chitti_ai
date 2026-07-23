from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class IdentityProfile:
    name: str = "User"
    language: str = "en-US"
    timezone: str = "UTC"
    location: Optional[str] = None
    email: Optional[str] = None


@dataclass
class BehaviorProfile:
    working_hours: str = "09:00-17:00"
    meeting_style: str = "Standard"
    daily_routine: str = "Standard"
    email_habits: str = "Standard"
    productivity_pattern: str = "Standard"


@dataclass
class PreferenceProfile:
    favorite_ide: str = "VS Code"
    preferred_browser: str = "Chrome"
    favorite_voice: str = "Default"
    favorite_apps: List[str] = field(default_factory=list)
    theme: str = "Dark"
