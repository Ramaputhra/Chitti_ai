from dataclasses import dataclass

@dataclass
class WidgetTheme:
    """
    S36D-2: Widget Visual Styling parameters enforcing canonical CHITTI Design System:
    Rounded Corners 10px, Noto Sans typography, Soft Shadow, Glass Blur, Minimal Borders.
    """
    corner_radius_px: int = 10
    font_family: str = "Noto Sans, Segoe UI Variable, Noto Sans CJK"
    soft_shadow: str = "0 8px 32px rgba(0, 0, 0, 0.25)"
    glass_blur_px: int = 16
    border_style: str = "1px solid rgba(255, 255, 255, 0.12)"
    accent_color: str = "#89B4FA"
