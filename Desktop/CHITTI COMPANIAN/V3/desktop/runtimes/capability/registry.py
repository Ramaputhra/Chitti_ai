from typing import Dict, Optional
from desktop.runtimes.capability.descriptors import CapabilityDescriptor

class CapabilityRegistry:
    """Stores purely immutable CapabilityDescriptors."""
    def __init__(self):
        self._capabilities: Dict[str, CapabilityDescriptor] = {}

    def register(self, descriptor: CapabilityDescriptor) -> None:
        self._capabilities[descriptor.id] = descriptor

    def resolve(self, action: str) -> Optional[CapabilityDescriptor]:
        return self._capabilities.get(action)
        
    def resolve_by_action_name(self, action_name: str) -> Optional[CapabilityDescriptor]:
        for desc in self._capabilities.values():
            if desc.action_name == action_name:
                return desc
        return None
        
    def get_all(self):
        return list(self._capabilities.values())
