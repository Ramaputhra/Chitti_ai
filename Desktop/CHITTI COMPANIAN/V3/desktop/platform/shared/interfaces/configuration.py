from typing import Any, Protocol

class IConfigurationService(Protocol):
    """
    Interface for the CHITTI Configuration Service.
    Defines the standard contract for accessing configuration.
    """

    def load(self, config_path: str | None = None) -> None:
        """Loads configuration from file, env vars, and secrets."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a configuration value."""
        ...

    def set_override(self, key: str, value: Any) -> None:
        """Sets a runtime override that takes precedence over all other layers."""
        ...

    def validate(self) -> bool:
        """Validates the current configuration state against a schema."""
        ...
