from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import IService


class ICapabilityResolver(IService):
    """
    Maps a flat tool name (e.g. ReadFile) to its authoritative Capability implementation.
    """
    def resolve_capability_for_tool(self, tool_name: str) -> ICapability:
        ...
