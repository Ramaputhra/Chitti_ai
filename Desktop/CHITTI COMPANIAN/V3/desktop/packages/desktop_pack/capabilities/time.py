import uuid
from datetime import datetime
from typing import List

from desktop.models.capability import (
    CanonicalCapabilityOutput,
    ExecutionResult as CapExecutionResult,
    VerificationResult,
    PresentationDescriptor,
    MemoryCandidate
)
from desktop.models.conversation import ConversationArtifact

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor

class TimeCapability(ICapability):
    """
    Time Capability (Phase 1).
    Fetches the current system time and produces the canonical capability output.
    """
    def __init__(self):
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "TimeCapability"

    @property
    def capability_id(self) -> str:
        return "cap_time_query"

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
                name="get_time",
                description="Gets the current system time.",
                parameters={}
            )
        ]

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name=self.name,
            version="1.0",
            category="System",
            tools=self.discover_tools(),
            description="Time fetching capability."
        )

    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name == "get_time"

    def cancel(self, invocation_id: str) -> None:
        pass

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if not self.validate(invocation):
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Invalid tool."])

        # Execution
        current_time = datetime.now()
        timezone = "UTC" # Or local timezone implementation
        
        cap_exec_result = CapExecutionResult(
            success=True,
            payload={"time": current_time.isoformat(), "timezone": timezone}
        )
        
        # Verification (Trivial for Time, as it reads local system state)
        verify_result = VerificationResult(
            verified=True,
            evidence_ids=["system_clock"],
            verification_strategy="trivial"
        )
        
        # Conversation Artifact
        artifact = ConversationArtifact(
            artifact_id=str(uuid.uuid4()),
            artifact_type="TimeArtifact",
            capability_id=self.capability_id,
            timestamp=current_time,
            summary=f"The current time is {current_time.strftime('%H:%M:%S')}",
            structured_result=cap_exec_result.payload,
            referenced_entities=[],
            supported_followup_actions=["Explain", "Convert Timezone", "Presentation"],
            presentation_available=True,
            expiration_policy="transient",
            confidence=1.0
        )
        
        # Presentation Descriptor (Delegates to Presentation Engine)
        pres_descriptor = PresentationDescriptor(
            experience_id="exp_time",
            recipe_id="recipe_digital_clock",
            layout_data={"time_str": current_time.strftime('%H:%M')}
        )
        
        # Memory Candidate
        mem_candidate = MemoryCandidate(
            activity_type="System Query",
            workspace_hint="System Shell",
            related_entities=["Time"],
            timestamp=current_time
        )
        
        canonical_out = CanonicalCapabilityOutput(
            execution_result=cap_exec_result,
            verification_result=verify_result,
            conversation_artifact=artifact,
            presentation_descriptor=pres_descriptor,
            memory_candidate=mem_candidate
        )
        
        return ExecutionResult(status=ExecutionStatus.SUCCESS, data=canonical_out)
