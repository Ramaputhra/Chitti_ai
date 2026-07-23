import os
from typing import Any, Dict

import yaml

from desktop.platform.shared.interfaces.configuration import IConfigurationService


class ConfigurationService(IConfigurationService):
    """
    Concrete implementation of the Configuration Service.
    Resolution Order: Overrides -> Env Vars -> File
    """

    def __init__(self) -> None:
        self._file_config: Dict[str, Any] = {}
        self._overrides: Dict[str, Any] = {}

    def load(self, config_path: str | None = None) -> None:
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self._file_config = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        # 1. Overrides
        if key in self._overrides:
            return self._overrides[key]

        # 2. Env Vars (look for CHITTI_ prefixed vars)
        env_key = f"CHITTI_{key.upper().replace('.', '_')}"
        if env_key in os.environ:
            return os.environ[env_key]

        # 3. File Config (handle dot notation e.g., 'app.theme')
        parts = key.split(".")
        current = self._file_config
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default

        return current

    def set_override(self, key: str, value: Any) -> None:
        self._overrides[key] = value

    def validate(self) -> bool:
        # TODO: Implement pydantic schema validation for production readiness
        return True
