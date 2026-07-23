from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.ai import ExecutionPlan


class IWorkflowExecutor(IService):
    """
    Executes a multi-step ExecutionPlan sequentially, communicating
    with the ToolManager for individual steps.
    """
    def execute_plan(self, plan: ExecutionPlan) -> None:
        ...
