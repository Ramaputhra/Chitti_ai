from typing import Any, Dict

from desktop.platform.shared.interfaces.executor import IExecutor
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.tool_manager import IToolManager
from desktop.platform.shared.models.ai import ExecutionPlan


class Executor(IExecutor):
    def __init__(self, tool_manager: IToolManager, logger: ILoggingService) -> None:
        self.tool_manager = tool_manager
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "Executor"

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
        return {}

    def execute_plan(self, plan: ExecutionPlan) -> None:
        self.logger.info(f"Executor running plan with {len(plan.steps)} steps")
        for step in plan.steps:
            if self.tool_manager.validate(step):
                self.logger.info(f"Executing tool {step.tool_name} via ToolManager")
                result = self.tool_manager.execute(step)
                self.logger.info(f"Tool {step.tool_name} completed with status {result.status.name}")
            else:
                self.logger.error(f"Validation failed for tool {step.tool_name}")
