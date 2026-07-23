import logging
from typing import Dict, Optional
from desktop.ui.themes.theme_registry import ThemeRegistry, UITheme

logger = logging.getLogger(__name__)

class ThemeManager:
    """
    S36D-1: Theme Manager overseeing Dark, Light, System themes and live switching.
    """
    def __init__(self):
        self._active_theme = ThemeRegistry.DARK

    @property
    def active_theme(self) -> UITheme:
        return self._active_theme

    def set_theme(self, name: str) -> bool:
        theme = ThemeRegistry.THEMES.get(name)
        if theme:
            self._active_theme = theme
            logger.info(f"[ThemeManager] Switched active UI Theme to '{name}'")
            return True
        return False
