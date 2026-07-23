"""
Platform shared capability interface.

This module re-exports from the canonical location in desktop.app.capability_contracts
for backward compatibility with platform-level code.
"""
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult
from desktop.platform.shared.models.tool import ToolDescriptor

# Import canonical types
from desktop.app.capability_contracts import ICapability as CanonicalICapability

# Re-export for backward compatibility
ICapability = CanonicalICapability


class ICapabilityRegistry(IService):
    """
    Registry for managing all operational capabilities.
    """
    @abstractmethod
    def register_capability(self, capability: ICapability) -> None:
        """Register a capability in the registry."""
        pass

    @abstractmethod
    def get_capability(self, name: str) -> Optional[ICapability]:
        """Get a registered capability by name."""
        pass

    @abstractmethod
    def list_capabilities(self) -> List[ICapability]:
        """List all registered capabilities."""
        pass
    
    @abstractmethod
    def discover_tools(self) -> List[ToolDescriptor]:
        """Discover all tools from all registered capabilities."""
        pass
