from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult
from desktop.platform.shared.models.tool import ToolDescriptor


class ICapability(IService):
    """
    Standard interface for all Operating Capabilities (e.g. Filesystem, Process).
    This is the primary capability interface used throughout the platform.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the capability."""
        pass
    
    @abstractmethod
    def discover_tools(self) -> List[ToolDescriptor]:
        """Discover available tools this capability provides."""
        pass

    @abstractmethod
    def validate(self, invocation: ToolInvocation) -> bool:
        """Validate if the invocation can be executed."""
        pass

    @abstractmethod
    async def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        """Execute the capability with the given invocation and context."""
        pass

    def cancel(self, invocation_id: str) -> None:
        """Cancel an in-progress execution."""
        pass

    @abstractmethod
    def describe(self) -> CapabilityDescriptor:
        """Return metadata about this capability."""
        pass

    def health_check(self) -> Dict[str, Any]:
        """Return health status of this capability."""
        return {"status": "healthy", "capability": self.name}


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
