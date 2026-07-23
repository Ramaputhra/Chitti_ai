from typing import Any, Dict, List, Optional

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.capability_registry import IRuntimeCapabilityRegistry
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState


class RuntimeCapabilityRegistry(IRuntimeCapabilityRegistry):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._capabilities: Dict[str, ICapability] = {}

    @property
    def name(self) -> str:
        return "RuntimeCapabilityRegistry"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"registered_capabilities": len(self._capabilities)}

    def register_capability(self, capability: ICapability) -> None:
        cap_desc = capability.describe()
        cap_name = cap_desc.get("name") if isinstance(cap_desc, dict) else getattr(cap_desc, "name", str(capability))
        tools = cap_desc.get("tools", []) if isinstance(cap_desc, dict) else getattr(cap_desc, "tools", [])
        self._capabilities[cap_name] = capability
        self.logger.info(f"Registered Capability: {cap_name} with {len(tools)} tools")

    def get_capability(self, name: str) -> Optional[ICapability]:
        return self._capabilities.get(name)

    def get_all_capabilities(self) -> List[ICapability]:
        return list(self._capabilities.values())
