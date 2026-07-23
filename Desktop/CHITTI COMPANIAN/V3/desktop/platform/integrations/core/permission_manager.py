from typing import Any, Dict

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.permission_manager import IPermissionManager
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.execution import ExecutionContext
from desktop.platform.shared.models.security import PermissionDecision, PermissionResult


class PermissionManager(IPermissionManager):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "PermissionManager"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> Dict[str, Any]:
        return {}

    def evaluate(self, invocation: ToolInvocation, context: ExecutionContext) -> PermissionResult:
        self.logger.info(f"Evaluating permissions for tool {invocation.tool_name}")
        return PermissionResult(decision=PermissionDecision.ALLOW, reason="Default allow")
