from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.execution import ExecutionContext
from desktop.platform.shared.models.security import PermissionResult


class IPermissionManager(IService):
    """
    Evaluates whether an execution context is authorized to perform a tool invocation.
    Answers: Can this be executed?
    """
    def evaluate(self, invocation: ToolInvocation, context: ExecutionContext) -> PermissionResult:
        ...
