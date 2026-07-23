import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from desktop.models.presentation import PresentationBundle, SupportedRenderer

@dataclass
class RendererCapabilities:
    """
    S32H: Declarative capabilities exported by renderers.
    """
    supports_streaming: bool = False
    supports_animation: bool = False
    supports_audio: bool = False
    supports_images: bool = False
    supports_interaction: bool = False
    supports_incremental_updates: bool = False

@dataclass
class RendererMetadata:
    """
    S32H: Metadata exported by renderers for discovery and resolution.
    """
    renderer_name: str
    renderer_version: str = "1.0.0"
    renderer_type: str = "GENERIC"
    supported_mime_types: List[str] = field(default_factory=lambda: ["application/json"])
    supported_bundle_types: List[str] = field(default_factory=lambda: ["ANALYTICS"])

@dataclass
class RendererExecutionContext:
    """
    S32H: Execution context provided to renderers during dispatch.
    """
    presentation_id: str
    bundle_id: str
    renderer_configuration: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    execution_deadline: Optional[float] = None

@dataclass
class RendererOutput:
    """
    S32H: Canonical output contract returned by every renderer.
    Contains zero runtime references or database handles.
    """
    renderer_id: str
    renderer_type: str
    mime_type: str
    payload: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    warnings: List[str] = field(default_factory=list)

class BaseRenderer(ABC):
    """
    S32H: Universal Base Renderer Lifecycle Contract.
    All current and future renderers inherit from BaseRenderer.
    """
    def __init__(self):
        self.context: Optional[RendererExecutionContext] = None
        self._initialized = False

    def initialize(self, context: Optional[RendererExecutionContext] = None) -> bool:
        self.context = context
        self._initialized = True
        return True

    def prepare(self, bundle: PresentationBundle) -> bool:
        return True

    @abstractmethod
    def render(self, bundle: PresentationBundle, context: Optional[RendererExecutionContext] = None) -> RendererOutput:
        pass

    def finalize(self) -> bool:
        return True

    def shutdown(self) -> bool:
        self._initialized = False
        return True

    def get_metadata(self) -> RendererMetadata:
        return RendererMetadata(renderer_name=self.__class__.__name__)

    def get_capabilities(self) -> RendererCapabilities:
        return RendererCapabilities()
