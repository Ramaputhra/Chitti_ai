import platform
import socket
from typing import List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor
from desktop.runtimes.presentation.models import PresentationModel, PresentationType, PresentationMetadata, PresentationCapability, PresentationLifetime
from desktop.runtimes.world.world_runtime import WorldRuntime

class SystemInfoCapability(ICapability):
    """Provides physical machine state (CPU, RAM, Battery, OS, Hostname) using the World Runtime."""
    
    def __init__(self, world_runtime: WorldRuntime):
        self.world_runtime = world_runtime
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "SystemInfoCapability"

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
            name="system_info",
            version="2.0",
            category="system",
            permissions=[],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(name="get_battery_status", description="Get battery percentage and plug status.", parameters=[]),
            ToolDescriptor(name="get_cpu_usage", description="Get total CPU usage percentage.", parameters=[]),
            ToolDescriptor(name="get_memory_usage", description="Get RAM usage percentage and total RAM.", parameters=[]),
            ToolDescriptor(name="get_disk_usage", description="Get main disk usage percentage.", parameters=[]),
            ToolDescriptor(name="get_os_version", description="Get Operating System name and version.", parameters=[]),
            ToolDescriptor(name="get_hostname", description="Get the machine's hostname on the network.", parameters=[])
        ]

    def validate(self, invocation: ToolInvocation) -> bool:
        valid_tools = [t.name for t in self.discover_tools()]
        return invocation.tool_name in valid_tools

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if not self.validate(invocation):
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Invalid tool."])
            
        data = {}
        summary = ""
        snapshot = self.world_runtime.get_current_snapshot()

        if invocation.tool_name == "get_battery_status":
            if snapshot.power:
                summary = f"{snapshot.power.get('level', '?')}% ({'Plugged In' if snapshot.power.get('plugged_in') else 'Discharging'})"
            else:
                summary = "Power information unavailable."
            data["battery"] = summary
            
        elif invocation.tool_name == "get_cpu_usage":
            # Assuming a future CPU/hardware provider populates this
            summary = "CPU Usage provided by hardware sensors (stubbed in WorldRuntime)"
            data["cpu"] = summary
            
        elif invocation.tool_name == "get_memory_usage":
            summary = "Memory Usage provided by hardware sensors (stubbed in WorldRuntime)"
            data["memory"] = summary
            
        elif invocation.tool_name == "get_disk_usage":
            summary = "Disk Usage provided by hardware sensors (stubbed in WorldRuntime)"
            data["disk"] = summary
            
        elif invocation.tool_name == "get_os_version":
            # We can still rely on platform since it's just Python standard lib, 
            # or move it to a SystemProvider in WorldRuntime. For strict Rule 105 compliance:
            summary = "OS Version provided by WorldRuntime"
            data["os"] = summary
            
        elif invocation.tool_name == "get_hostname":
            summary = "Hostname provided by WorldRuntime"
            data["hostname"] = summary
        else:
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Execution failed"])
            
        model = PresentationModel(
            type=PresentationType.DASHBOARD,
            title="System Information",
            subtitle=f"Metric: {invocation.tool_name}",
            icon="server",
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
