from dataclasses import dataclass
from typing import Dict

@dataclass
class UITheme:
    name: str
    bg_color: str
    text_color: str
    accent_color: str
    glassmorphism_opacity: float

class ThemeRegistry:
    """
    S36D-1: Theme Registry supporting Dark, Light, System themes.
    Future themes registration supported without code changes.
    """
    DARK = UITheme("Dark", bg_color="#1E1E2E", text_color="#F5E0DC", accent_color="#89B4FA", glassmorphism_opacity=0.85)
    LIGHT = UITheme("Light", bg_color="#FFFFFF", text_color="#181825", accent_color="#1E66F5", glassmorphism_opacity=0.90)
    SYSTEM = UITheme("System", bg_color="#1E1E2E", text_color="#F5E0DC", accent_color="#89B4FA", glassmorphism_opacity=0.85)

    THEMES: Dict[str, UITheme] = {
        "Dark": DARK,
        "Light": LIGHT,
        "System": SYSTEM
    }
