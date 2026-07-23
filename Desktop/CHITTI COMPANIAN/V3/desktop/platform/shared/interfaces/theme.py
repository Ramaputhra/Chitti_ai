from typing import Protocol


class IThemeManager(Protocol):
    """
    Manages the application theme.
    """
    def apply_theme(self, theme_name: str) -> None:
        """Applies a theme by name (e.g., 'dark', 'light')."""
        ...

    def current_theme(self) -> str:
        """Returns the current theme name."""
        ...
