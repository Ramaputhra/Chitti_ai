from typing import Any, Protocol


class ISettingsManager(Protocol):
    """
    Manages persistent, typed user preferences and runtime settings.
    """
    def initialize(self) -> None:
        """Loads settings from disk."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a setting by key."""
        ...

    def set(self, key: str, value: Any) -> None:
        """Sets a setting and publishes Settings.Changed if modified."""
        ...

    def has(self, key: str) -> bool:
        """Checks if a setting exists."""
        ...
