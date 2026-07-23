from typing import List

from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.runtimes.capability.base import BaseCapability
from desktop.platform.shared.interfaces.event_bus import IEventBus, Event

class NotificationCapability(BaseCapability):
    """
    Emits Notification.Emitted events which the Presence Runtime can intercept to display toasts.
    """
    def __init__(self, event_bus: IEventBus):
        super().__init__()
        self.event_bus = event_bus
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "NotificationCapability"

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
            name="notification",
            version="1.0",
            category="system",
            permissions=["notifications"],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="show_notification",
                description="Displays a system notification toast.",
                parameters=[
                    ToolParameter(name="title", type="string", description="Title of the notification.", required=True),
                    ToolParameter(name="message", type="string", description="Body text of the notification.", required=True)
                ]
            )
        ]

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if invocation.tool_name == "show_notification":
            title = invocation.parameters.get("title", "Notification")
            message = invocation.parameters.get("message", "")
            
            try:
                # Emit event, letting Presence Runtime or a dedicated Notification UI handle it
                event = Event(
                    name="Notification.Emitted",
                    source="NotificationCapability",
                    payload={"title": title, "message": message}
                )
                self.event_bus.publish(event)
                
                return ExecutionResult(success=True, output="Notification emitted successfully.")
            except Exception as e:
                return ExecutionResult(success=False, error=str(e))
                
        return ExecutionResult(success=False, error=f"Unknown tool: {invocation.tool_name}")
