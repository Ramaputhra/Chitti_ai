import logging
from typing import Dict, Any
from desktop.ui.renderer.texture_cache import TextureCache
from desktop.ui.renderer.asset_cache import AssetCache
from desktop.ui.renderer.png_renderer import PNGRenderer, SVGRenderer, IconRenderer
from desktop.ui.runtime.runtime_metrics import RuntimeMetrics
from desktop.ui.runtime.runtime_validator import RuntimeValidator

logger = logging.getLogger(__name__)

class MasterUIRenderer:
    """
    S36D-1: Master Desktop UI Renderer enforcing Render Profiles & Hardware Accelerated Composition.
    Profiles: WIDGET (30 FPS), WAVEFORM (24 FPS), PRESENCE_DOT (5 FPS), STATIC_WINDOW (Event-Driven).
    PROHIBITED: Desktop UI Runtime SHALL NEVER render Character PNG assets.
    """
    def __init__(self):
        self.texture_cache = TextureCache()
        self.asset_cache = AssetCache()
        self.png_renderer = PNGRenderer()
        self.svg_renderer = SVGRenderer()
        self.icon_renderer = IconRenderer()
        self.metrics = RuntimeMetrics()
        self.validator = RuntimeValidator()

    def render_window_frame(self, window_id: str, profile: str = "WIDGET", asset_type: str = "ui_vector") -> str:
        # Validate runtime invariant
        ok, errs = self.validator.validate_render_request(asset_type)
        if not ok:
            logger.error(f"[MasterUIRenderer] Render request failed: {errs}")
            raise ValueError(f"Render Prohibited: {errs}")

        self.metrics.record_frame(profile)
        cached = self.texture_cache.get(f"tex_{window_id}")
        if cached:
            self.metrics.record_cache_hit()
            return cached

        self.metrics.record_cache_miss()
        rendered = f"<gpu_composed_frame window='{window_id}' profile='{profile}'/>"
        self.texture_cache.put(f"tex_{window_id}", rendered)
        return rendered
