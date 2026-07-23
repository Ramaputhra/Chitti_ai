import time
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

try:
    from desktop.models.presentation_models import *
except ImportError:
    pass

try:
    from desktop.models.interaction import *
except ImportError:
    pass

class AvatarState(Enum):
    IDLE = "IDLE"
    OPERATING = "OPERATING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"
    HAPPY = "HAPPY"
    ERROR = "ERROR"

@dataclass
class AvatarStateChanged:
    state: AvatarState
    timestamp: float = field(default_factory=time.time)

@dataclass
class RenderedExpression:
    format_name: str
    content: Any
    timestamp: float = field(default_factory=time.time)

class BundleType(str, Enum):
    ANALYTICS = "ANALYTICS"
    NAVIGATION = "NAVIGATION"
    BROWSER = "BROWSER"
    VISION = "VISION"
    OCR = "OCR"
    REMINDER = "REMINDER"
    CALENDAR = "CALENDAR"
    SYSTEM = "SYSTEM"

class ExperienceType(str, Enum):
    DASHBOARD = "DASHBOARD"
    OVERLAY = "OVERLAY"
    VOICE = "VOICE"
    MULTIMODAL = "MULTIMODAL"
    NOTIFICATION = "NOTIFICATION"

class SupportedRenderer(str, Enum):
    DASHBOARD_RENDERER = "DASHBOARD_RENDERER"
    VOICE_RENDERER = "VOICE_RENDERER"
    AVATAR_RENDERER = "AVATAR_RENDERER"
    NANO_RENDERER = "NANO_RENDERER"
    TEXT_RENDERER = "TEXT_RENDERER"

@dataclass
class PresentationBundle:
    """
    S32D: Universal base PresentationBundle contract.
    Defines canonical interface separating domain runtimes from presentation rendering layers.
    Pure domain data container; contains ZERO UI rendering logic, HTML, CSS, or narration text.
    """
    bundle_id: str
    bundle_type: BundleType = BundleType.SYSTEM
    experience_type: ExperienceType = ExperienceType.DASHBOARD
    timestamp: float = field(default_factory=time.time)
    supported_renderers: List[SupportedRenderer] = field(default_factory=lambda: [SupportedRenderer.DASHBOARD_RENDERER])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "bundle_type": self.bundle_type.value if isinstance(self.bundle_type, Enum) else str(self.bundle_type),
            "experience_type": self.experience_type.value if isinstance(self.experience_type, Enum) else str(self.experience_type),
            "timestamp": self.timestamp,
            "supported_renderers": [
                r.value if isinstance(r, Enum) else str(r) for r in self.supported_renderers
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PresentationBundle':
        b_type = BundleType(data.get("bundle_type", BundleType.SYSTEM.value))
        exp_type = ExperienceType(data.get("experience_type", ExperienceType.DASHBOARD.value))
        renderers = [SupportedRenderer(r) for r in data.get("supported_renderers", [SupportedRenderer.DASHBOARD_RENDERER.value])]
        return cls(
            bundle_id=data.get("bundle_id", ""),
            bundle_type=b_type,
            experience_type=exp_type,
            timestamp=data.get("timestamp", time.time()),
            supported_renderers=renderers
        )

def validate_presentation_bundle(bundle: Any) -> bool:
    """
    S32D: Bundle validation utility ensuring structural compliance with PresentationBundle contract.
    """
    if not bundle:
        return False
    if not isinstance(bundle, PresentationBundle) and not issubclass(bundle.__class__, PresentationBundle):
        return False
    if not getattr(bundle, "bundle_id", None):
        return False
    if not getattr(bundle, "bundle_type", None):
        return False
    if not getattr(bundle, "experience_type", None):
        return False
    if not getattr(bundle, "supported_renderers", None):
        return False
    return True
