import logging
from typing import Dict, Tuple, Any, Optional
from desktop.models.presentation import BundleType, ExperienceType, SupportedRenderer
from desktop.runtimes.presentation.contracts import IPresentationExperience, IPresentationRenderer

logger = logging.getLogger(__name__)

class ExperienceRegistry:
    """
    S32E: Registry-driven experience mapping (bundle_type + experience_type -> experience).
    Contains ZERO hardcoded domain type checks.
    """
    def __init__(self):
        self._registry: Dict[Tuple[str, str], Any] = {}

    def _normalize_key(self, b_type: Any, e_type: Any) -> Tuple[str, str]:
        b_str = b_type.value if hasattr(b_type, "value") else str(b_type)
        e_str = e_type.value if hasattr(e_type, "value") else str(e_type)
        return (b_str.upper(), e_str.upper())

    def register_experience(self, bundle_type: Any, experience_type: Any, experience: Any):
        key = self._normalize_key(bundle_type, experience_type)
        self._registry[key] = experience
        logger.info(f"[ExperienceRegistry] Registered experience '{experience}' for {key}.")

    def get_experience(self, bundle_type: Any, experience_type: Any) -> Optional[Any]:
        key = self._normalize_key(bundle_type, experience_type)
        return self._registry.get(key)

class RendererRegistry:
    """
    S32E/S32H: Registry-driven renderer dispatch and discovery mapping.
    Contains ZERO hardcoded renderer dispatch calls.
    """
    def __init__(self):
        self._registry: Dict[str, Any] = {}

    def _normalize_key(self, renderer_key: Any) -> str:
        return renderer_key.value if hasattr(renderer_key, "value") else str(renderer_key).upper()

    def register_renderer(self, renderer_key: Any, renderer: Any):
        key = self._normalize_key(renderer_key)
        self._registry[key] = renderer
        logger.info(f"[RendererRegistry] Registered renderer '{renderer}' for '{key}'.")

    def get_renderer(self, renderer_key: Any) -> Optional[Any]:
        key = self._normalize_key(renderer_key)
        return self._registry.get(key)

    def get_metadata(self, renderer_key: Any) -> Optional[Any]:
        renderer = self.get_renderer(renderer_key)
        if renderer and hasattr(renderer, "get_metadata"):
            return renderer.get_metadata()
        return None

    def get_capabilities(self, renderer_key: Any) -> Optional[Any]:
        renderer = self.get_renderer(renderer_key)
        if renderer and hasattr(renderer, "get_capabilities"):
            return renderer.get_capabilities()
        return None

    def find_renderers_by_capability(self, capability_name: str) -> Dict[str, Any]:
        matched = {}
        for k, renderer in self._registry.items():
            if hasattr(renderer, "get_capabilities"):
                caps = renderer.get_capabilities()
                if getattr(caps, capability_name, False):
                    matched[k] = renderer
        return matched
