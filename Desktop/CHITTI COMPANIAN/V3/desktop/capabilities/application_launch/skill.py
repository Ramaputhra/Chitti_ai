import logging
from typing import List, Any
from desktop.platform.shared.interfaces.skill import ISkill
from desktop.platform.shared.models.intent import Intent
from desktop.capabilities.application_launch.adapter import ApplicationLaunchAdapter
from desktop.runtimes.workflow.models import ExecutionResult, ExecutionStatus

logger = logging.getLogger(__name__)

class ApplicationLaunchSkill(ISkill):
    """
    Skill for launching desktop applications.
    """
    def __init__(self):
        self._adapter = ApplicationLaunchAdapter()

    def id(self) -> str:
        return "application.launch"

    def name(self) -> str:
        return "Application Launch"

    def version(self) -> str:
        return "1.0.0"

    def supported_intents(self) -> List[str]:
        return ["application.launch"]

    def execute(self, intent: Intent) -> ExecutionResult:
        app_name = intent.parameters.get("application") if intent.parameters else None
        
        if not app_name:
            return ExecutionResult(
                status=ExecutionStatus.FAILURE,
                error_message="Missing required parameter: application"
            )
            
        return self._adapter.execute(app_name)

    def health_check(self) -> bool:
        return True
