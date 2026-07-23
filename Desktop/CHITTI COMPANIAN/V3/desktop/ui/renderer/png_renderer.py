import logging

logger = logging.getLogger(__name__)

class SVGRenderer:
    """S36D-1: Format-Specific SVG Renderer."""
    def render_svg(self, svg_content: str) -> str:
        return f"<svg_rendered>{svg_content[:30]}...</svg_rendered>"

class PNGRenderer:
    """S36D-1: Format-Specific UI Asset PNG Renderer (Desktop UI assets ONLY, never Character PNGs)."""
    def render_png(self, asset_path: str) -> str:
        if "character" in asset_path.lower():
            raise ValueError("PROHIBITED: Desktop UI Runtime SHALL NEVER render Character PNG assets!")
        return f"<png_rendered>{asset_path}</png_rendered>"

class IconRenderer:
    """S36D-1: Format-Specific Vector & Icon Renderer."""
    def render_icon(self, icon_name: str) -> str:
        return f"<icon_rendered>{icon_name}</icon_rendered>"
