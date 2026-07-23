import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class CapabilityRegistry:
    """
    Maintains three distinct stores of capabilities to prevent pollution of built-ins.
    """
    def __init__(self):
        self._built_in: Dict[str, Any] = {}
        self._learned: Dict[str, Any] = {}
        self._user_imported: Dict[str, Any] = {}

    def register_built_in(self, name: str, capability: Any) -> None:
        self._built_in[name] = capability
        logger.debug(f"Registered built-in primitive: {name}")

    def register_learned(self, name: str, capability: Any) -> None:
        self._learned[name] = capability
        logger.info(f"Registered learned capability: {name}")

    def register_imported(self, name: str, capability: Any) -> None:
        self._user_imported[name] = capability
        logger.info(f"Registered user-imported capability: {name}")

    def get_capability(self, name: str) -> Any:
        # Hierarchy: Imported overrides Learned overrides Built-In
        if name in self._user_imported:
            return self._user_imported[name]
        if name in self._learned:
            return self._learned[name]
        if name in self._built_in:
            return self._built_in[name]
        return None
