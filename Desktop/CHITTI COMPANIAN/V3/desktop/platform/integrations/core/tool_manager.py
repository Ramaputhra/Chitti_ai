from typing import Any, Dict, List, Optional

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.tool_manager import IToolManager
from desktop.platform.shared.models.ai import ToolInvocation, ToolResult, ToolResultStatus
from desktop.platform.shared.models.tool import ToolDescriptor


class ToolManager(IToolManager):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._tools: Dict[str, ToolDescriptor] = {}

    @property
    def name(self) -> str:
        return "ToolManager"

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
        return {"registered_tools": len(self._tools)}

    def discover(self, category: Optional[str] = None) -> List[ToolDescriptor]:
        if category:
            return [t for t in self._tools.values() if t.category == category]
        return list(self._tools.values())

    def describe(self, name: str) -> Optional[ToolDescriptor]:
        return self._tools.get(name)

    def validate(self, invocation: ToolInvocation) -> bool:
        return True

    def execute(self, invocation: ToolInvocation) -> ToolResult:
        self.logger.info(f"Executing tool: {invocation.tool_name}")
        return ToolResult(
            status=ToolResultStatus.FINAL,
            data={"response": f"Mock executed {invocation.tool_name}"}
        )

    def cancel(self, invocation_id: str) -> None:
        self.logger.info(f"Cancelling tool execution {invocation_id}")
