from typing import Any, Dict, List

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.expression_model import ExpressionModel


class IExpressionProvider(IService):
    """
    Standard interface for all hardware output actuators.
    Providers may never interpret intent; they strictly execute
    the unified `ExpressionModel` mapped to their supported domain.
    """
    def supports(self) -> List[str]:
        """Returns the keys in ExpressionModel this provider cares about (e.g., 'eyes_state')."""
        ...

    def execute(self, model: ExpressionModel) -> None:
        """Executes the exact state requested by the Scheduler."""
        ...

    def cancel(self) -> None:
        """Immediately halts ongoing actuation safely."""
        ...
