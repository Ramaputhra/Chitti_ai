from dataclasses import dataclass, field
from typing import Any, Dict, List

from desktop.platform.shared.models.perception_artifact import PerceptionArtifact


@dataclass
class ScreenArtifact(PerceptionArtifact):
    """Base class for artifacts originating from the Screen Runtime."""
    pass


@dataclass
class ScreenshotArtifact(ScreenArtifact):
    resolution: str = ""
    color_space: str = ""


@dataclass
class WindowArtifact(ScreenArtifact):
    """Represents a discrete OS window that was extracted from the ScreenModel."""
    app_name: str = ""
    active_task: str = ""
    bounding_box: List[int] = field(default_factory=list)


@dataclass
class UIElementArtifact(ScreenArtifact):
    """Represents a button, input field, or menu extracted from the ScreenModel."""
    element_type: str = ""
    text: str = ""
    is_focused: bool = False
    bounding_box: List[int] = field(default_factory=list)
