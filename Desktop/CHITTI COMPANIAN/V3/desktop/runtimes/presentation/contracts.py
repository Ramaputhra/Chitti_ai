import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from desktop.models.presentation import PresentationBundle, SupportedRenderer

@dataclass
class PresentationSession:
    """
    S32E: Presentation execution session tracking pipeline execution.
    """
    presentation_id: str
    bundle_id: str
    selected_experience: str
    selected_renderers: List[str] = field(default_factory=list)
    start_timestamp: float = field(default_factory=time.time)
    end_timestamp: float = 0.0
    execution_status: str = "INITIALIZED"  # "INITIALIZED", "RUNNING", "COMPLETED", "FAILED"

from desktop.runtimes.presentation.framework import RendererOutput

@dataclass
class PresentationResult:
    """
    S32E/S32H: Pure execution result returned by PresentationRuntime pipeline.
    Contains RendererOutputCollection (List[RendererOutput]).
    """
    presentation_id: str
    bundle_id: str
    success: bool
    outputs: List[RendererOutput] = field(default_factory=list)
    rendered_outputs: Dict[str, Any] = field(default_factory=dict)
    renderer_status: Dict[str, str] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    warnings: List[str] = field(default_factory=list)

class IPresentationExperience(ABC):
    """
    Abstract interface for registered presentation experiences.
    """
    @abstractmethod
    def get_experience_name(self) -> str:
        pass

class IPresentationRenderer(ABC):
    """
    Abstract interface for registered presentation renderers.
    """
    @abstractmethod
    def get_renderer_id(self) -> SupportedRenderer:
        pass

    @abstractmethod
    def render(self, bundle: PresentationBundle) -> Any:
        pass
