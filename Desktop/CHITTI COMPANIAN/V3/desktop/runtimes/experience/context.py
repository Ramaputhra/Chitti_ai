from dataclasses import dataclass
from typing import Any, Dict
from desktop.models.presentation import PresentationMemory, PresentationSession

@dataclass
class ExperienceContext:
    """
    Dedicated context passed to Experiences instead of the entire runtime (Rule 342).
    """
    session: PresentationSession
    presentation_memory: PresentationMemory
    widget_registry: Any
    interaction_router: Any
    theme: str
    user_preferences: Dict[str, Any]
    telemetry: Any
