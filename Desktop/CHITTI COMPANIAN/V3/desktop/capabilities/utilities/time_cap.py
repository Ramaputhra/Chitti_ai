import time
from datetime import datetime
from typing import List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor
from desktop.runtimes.presentation.models import PresentationModel, PresentationType, PresentationMetadata, PresentationCapability, PresentationLifetime


class TimeCapability(ICapability):
    """Provides current time, date, and timezone information."""
    
    def __init__(self):
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "TimeCapability"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> dict:
        return {"status": "healthy"}

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name="time",
            version="1.0",
            category="utilities",
            permissions=[],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(name="get_current_time", description="Get the current local time.", parameters=[]),
            ToolDescriptor(name="get_date", description="Get the current local date.", parameters=[]),
            ToolDescriptor(name="get_timezone_info", description="Get the local timezone and UTC offset.", parameters=[])
        ]

    def validate(self, invocation: ToolInvocation) -> bool:
        valid_tools = [t.name for t in self.discover_tools()]
        return invocation.tool_name in valid_tools

    def execute(self, *args, **kwargs) -> ExecutionResult:
        if args and hasattr(args[0], "tool_name"):
            invocation = args[0]
        else:
            action = kwargs.get("action")
            parameters = kwargs.get("parameters", {})
            invocation = ToolInvocation(tool_name=action, parameters=parameters)

        if not self.validate(invocation):
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Invalid tool."])

        now = datetime.now()
        data = {}
        summary = ""
        
        if invocation.tool_name == "get_current_time":
            summary = now.strftime("%I:%M %p")
            data["time"] = summary
            
        elif invocation.tool_name == "get_date":
            summary = now.strftime("%A, %B %d, %Y")
            data["date"] = summary
            
        elif invocation.tool_name == "get_timezone_info":
            tz_name = time.tzname[time.daylight]
            offset_hours = -time.timezone / 3600
            summary = f"Timezone: {tz_name} (UTC{offset_hours:+.1f})"
            data["timezone"] = summary
        else:
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Execution failed"])

        model = PresentationModel(
            type=PresentationType.CARDS,
            title="Date & Time",
            subtitle=summary,
            icon="clock",
            data=data,
            actions=[],
            metadata=PresentationMetadata(
                capabilities=[PresentationCapability.LIVE],
                lifetime=PresentationLifetime.TRANSIENT
            )
        )
        
        return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=summary, presentation=model)

    def cancel(self, invocation_id: str) -> None:
        pass
