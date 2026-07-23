import threading
import time
from typing import List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.event_bus import IEventBus, Event
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter


class TimerCapability(ICapability):
    """Provides a lightweight, in-memory timer that triggers a platform event."""
    
    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self._state = ServiceState.STOPPED
        self._active_timers = {}

    @property
    def name(self) -> str:
        return "TimerCapability"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self._active_timers.clear()

    def health_check(self) -> dict:
        return {"status": "healthy", "active_timers": len(self._active_timers)}

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name="timer",
            version="1.0",
            category="automation",
            permissions=[],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="set_timer", 
                description="Set a lightweight in-memory timer that fires after N seconds.", 
                parameters=[
                    ToolParameter(name="duration_seconds", type="integer", description="Duration in seconds.", required=True),
                    ToolParameter(name="message", type="string", description="The alert message for the timer.", required=True)
                ]
            )
        ]

    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name == "set_timer" and "duration_seconds" in invocation.parameters and "message" in invocation.parameters

    def execute(self, *args, **kwargs) -> ExecutionResult:
        if args and hasattr(args[0], "tool_name"):
            invocation = args[0]
        else:
            action = kwargs.get("action")
            parameters = kwargs.get("parameters", {})
            invocation = ToolInvocation(tool_name=action, parameters=parameters)

        if not self.validate(invocation):
            return ExecutionResult(success=False, error="Invalid tool.", output=None)

        try:
            duration = int(invocation.parameters["duration_seconds"])
            message = invocation.parameters["message"]
        except ValueError:
            return ExecutionResult(success=False, error="Invalid duration format.", output=None)

        timer_id = f"timer_{int(time.time())}"
        
        def _timer_callback():
            self._active_timers.pop(timer_id, None)
            # Wakes up the system via EventBus
            self._event_bus.publish(
                Event(
                    id="Timer.Completed", 
                    source="TimerCapability", 
                    payload={"timer_id": timer_id, "message": message}
                )
            )
            
        t = threading.Timer(duration, _timer_callback)
        t.daemon = True
        self._active_timers[timer_id] = t
        t.start()

        return ExecutionResult(success=True, output=f"Timer set for {duration} seconds with message: '{message}'.")

    def cancel(self, invocation_id: str) -> None:
        pass
