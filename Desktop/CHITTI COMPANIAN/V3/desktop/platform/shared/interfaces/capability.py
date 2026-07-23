from typing import Any, Dict, List

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult
from desktop.platform.shared.models.tool import ToolDescriptor


class ICapability(IService):
    """
    Standard interface for all Operating Capabilities (e.g. Filesystem, Process).
    """
    def discover_tools(self) -> List[ToolDescriptor]:
        ...

    def validate(self, invocation: ToolInvocation) -> bool:
        ...

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        ...

    def cancel(self, invocation_id: str) -> None:
        ...

    def describe(self) -> CapabilityDescriptor:
        ...

class ICapabilityRegistry(IService):
    """
    Registry for managing all operational capabilities.
    """
    def register_capability(self, capability: ICapability) -> None:
        ...

    def get_capability(self, name: str) -> ICapability:
        ...

    def list_capabilities(self) -> List[ICapability]:
        ...
