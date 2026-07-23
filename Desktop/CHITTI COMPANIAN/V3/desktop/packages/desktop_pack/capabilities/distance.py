import uuid
from datetime import datetime, timedelta
from typing import List

from desktop.models.capability import (
    CanonicalCapabilityOutput,
    ExecutionResult as CapExecutionResult,
    VerificationResult,
    PresentationDescriptor,
    MemoryCandidate
)
from desktop.models.conversation import NavigationArtifact

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor

class DistanceCapability(ICapability):
    """
    Distance Capability (Phase 1 & 2).
    Calculates static Distance/ETA between Origin and Destination.
    Generates the immutable NavigationArtifact consumed by NavigationCapability.
    """
    def __init__(self):
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "DistanceCapability"

    @property
    def capability_id(self) -> str:
        return "cap_distance_query"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> dict:
        return {"status": "healthy"}

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="get_distance",
                description="Get distance between points.",
                parameters={}
            )
        ]

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name=self.name,
            version="1.0",
            category="System",
            tools=self.discover_tools(),
            description="Distance querying capability."
        )

    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name == "get_distance"

    def cancel(self, invocation_id: str) -> None:
        pass

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if not self.validate(invocation):
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Invalid tool."])

        payload = invocation.arguments
        origin = payload.get("origin", "Current Location")
        destination = payload.get("destination", "Unknown Destination")
        
        return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Distance provider not implemented. Requires future feature sprint."])
