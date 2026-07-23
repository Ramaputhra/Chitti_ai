from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.ai import ExecutionPlan, LLMResponse


class IActionPlanner(IService):
    """
    Deterministically transforms parsed LLM responses into executable plans.
    Does NOT infer missing parameters.
    """
    def plan(self, response: LLMResponse) -> ExecutionPlan:
        """Returns a deterministically planned workflow for a given intent."""
        ...
