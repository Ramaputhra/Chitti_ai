from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.execution import ExecutionContext
from desktop.platform.shared.models.security import PermissionResult


class IRuntimePolicyEngine(IService):
    """
    Evaluates behavioral policies to determine if a requested tool execution is appropriate.
    Answers: Should this be executed?
    """
    def evaluate_policy(self, invocation: ToolInvocation, context: ExecutionContext) -> PermissionResult:
        ...
