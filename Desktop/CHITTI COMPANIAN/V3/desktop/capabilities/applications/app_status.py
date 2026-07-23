import sys
from typing import List

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.runtimes.presentation.models import PresentationModel, PresentationType, PresentationMetadata, PresentationCapability, PresentationLifetime


class ApplicationStatusCapability(ICapability):
    """Provides awareness of running desktop applications."""
    
    def __init__(self):
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "ApplicationStatusCapability"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> dict:
        return {"status": "healthy" if HAS_PSUTIL else "degraded (missing psutil)"}

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name="application_status",
            version="1.0",
            category="applications",
            permissions=[],
            tools=self.discover_tools(),
            health="healthy" if HAS_PSUTIL else "degraded",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(name="list_running_applications", description="Get a list of major running applications.", parameters=[]),
            ToolDescriptor(
                name="is_application_running", 
                description="Check if a specific application (like 'zoom', 'chrome', 'vscode') is running.", 
                parameters=[ToolParameter(name="app_name", type="string", description="Name of the application.", required=True)]
            )
        ]

    def validate(self, invocation: ToolInvocation) -> bool:
        if invocation.tool_name == "list_running_applications":
            return True
        elif invocation.tool_name == "is_application_running":
            return "app_name" in invocation.parameters
        return False

    def _get_app_processes(self) -> List[str]:
        apps = set()
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if name:
                    if sys.platform == "win32" and name.lower().endswith(".exe"):
                        name = name[:-4]
                    apps.add(name.lower())
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return list(apps)

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if not self.validate(invocation):
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Invalid tool."])

        if not HAS_PSUTIL:
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["psutil library is required for application status."])

        apps = self._get_app_processes()
        
        if invocation.tool_name == "list_running_applications":
            common_apps = ["chrome", "firefox", "edge", "safari", "zoom", "teams", "slack", "discord", "code", "spotify"]
            running_common = [a for a in apps if a in common_apps]
            summary = f"Found common running apps: {', '.join(running_common)}"
            
            model = PresentationModel(
                type=PresentationType.TABLE,
                title="Running Applications",
                subtitle="Common Apps",
                icon="view-list",
                data={"apps": running_common},
                actions=[],
                metadata=PresentationMetadata(
                    capabilities=[PresentationCapability.SORT],
                    lifetime=PresentationLifetime.MANUAL
                )
            )
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=summary, presentation=model)
            
        elif invocation.tool_name == "is_application_running":
            target = invocation.parameters["app_name"].lower()
            is_running = any(target in a for a in apps)
            status_str = "Running" if is_running else "Not Running"
            summary = f"{invocation.parameters['app_name']}: {status_str}"
            
            model = PresentationModel(
                type=PresentationType.REPORT,
                title="Application Status",
                subtitle=target,
                icon="application",
                data={"app": target, "status": status_str},
                actions=[],
                metadata=PresentationMetadata(
                    capabilities=[PresentationCapability.LIVE],
                    lifetime=PresentationLifetime.TRANSIENT
                )
            )
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=summary, presentation=model)

        return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Execution failed"])

    def cancel(self, invocation_id: str) -> None:
        pass
