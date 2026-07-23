from typing import List
import urllib.request
import urllib.parse

from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.runtimes.capability.base import BaseCapability
from desktop.runtimes.presentation.models import PresentationModel, PresentationType, PresentationMetadata, PresentationCapability, PresentationLifetime

class WeatherCapability(BaseCapability):
    """
    Fetches weather using the keyless wttr.in service.
    """
    def __init__(self):
        super().__init__()
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "WeatherCapability"

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
            name="weather",
            version="1.0",
            category="utilities",
            permissions=["network"],
            tools=self.discover_tools(),
            health="healthy",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="get_weather",
                description="Get current weather for a location.",
                parameters=[
                    ToolParameter(name="location", type="string", description="City name or zip code.", required=True)
                ]
            )
        ]

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if invocation.tool_name == "get_weather":
            location = invocation.parameters.get("location", "")
            if not location:
                return ExecutionResult(success=False, error="Location is required.")
                
            try:
                # wttr.in with format=3 returns "location: condition +temperature"
                url = f"https://wttr.in/{urllib.parse.quote(location)}?format=3"
                req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    weather_data = response.read().decode('utf-8').strip()
                    
                model = PresentationModel(
                    type=PresentationType.CARDS,
                    title=f"Weather in {location}",
                    subtitle="Current conditions",
                    icon="cloud-sun",
                    data={"text": weather_data},
                    actions=[],
                    metadata=PresentationMetadata(
                        capabilities=[PresentationCapability.LIVE],
                        lifetime=PresentationLifetime.TRANSIENT
                    )
                )
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    summary=f"Fetched weather for {location}.",
                    presentation=model
                )
            except Exception as e:
                return ExecutionResult(status=ExecutionStatus.FAILURE, errors=[str(e)])
                
        return ExecutionResult(status=ExecutionStatus.FAILURE, errors=[f"Unknown tool: {invocation.tool_name}"])
