import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

class PluginCoordinator:
    """S36E: Plugin Coordinator providing plugin registration hooks while remaining plugin-agnostic."""
    def __init__(self):
        self._hooks: Dict[str, Callable] = {}

    def register_hook(self, plugin_name: str, hook_func: Callable):
        self._hooks[plugin_name] = hook_func
        logger.info(f"[PluginCoordinator] Registered orchestration hook for plugin '{plugin_name}'")
