from typing import Any, Dict

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.capability_registry import IRuntimeCapabilityRegistry
from desktop.platform.shared.interfaces.capability_resolver import ICapabilityResolver
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState


class CapabilityResolver(ICapabilityResolver):
    def __init__(self, registry: IRuntimeCapabilityRegistry, logger: ILoggingService) -> None:
        self.registry = registry
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._cache: Dict[str, ICapability] = {}

    @property
    def name(self) -> str:
        return "CapabilityResolver"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self._cache.clear()
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"cache_size": len(self._cache)}

    def resolve_capability_for_tool(self, tool_name: str) -> ICapability:
        if tool_name in self._cache:
            return self._cache[tool_name]
        
        for cap in self.registry.get_all_capabilities():
            for tool in cap.discover_tools():
                if tool.name == tool_name:
                    self.logger.info(f"Resolved tool '{tool_name}' to Capability '{cap.name}'")
                    self._cache[tool_name] = cap
                    return cap
                    
        raise ValueError(f"No capability found providing tool: {tool_name}")
