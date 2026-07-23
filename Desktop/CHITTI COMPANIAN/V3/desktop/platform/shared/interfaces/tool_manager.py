from typing import List, Optional

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.ai import ToolInvocation, ToolResult
from desktop.platform.shared.models.tool import ToolDescriptor


class IToolManager(IService):
    """
    Central hub for registering and executing deterministic tools.
    """
    def discover(self, category: Optional[str] = None) -> List[ToolDescriptor]:
        ...

    def describe(self, name: str) -> Optional[ToolDescriptor]:
        ...

    def validate(self, invocation: ToolInvocation) -> bool:
        ...

    def execute(self, invocation: ToolInvocation) -> ToolResult:
        ...

    def cancel(self, invocation_id: str) -> None:
        ...
