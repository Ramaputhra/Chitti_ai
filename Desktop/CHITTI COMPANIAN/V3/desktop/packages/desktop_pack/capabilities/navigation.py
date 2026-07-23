import uuid
import asyncio
from datetime import datetime
from typing import List

from desktop.models.capability import (
    CanonicalCapabilityOutput,
    ExecutionResult as CapExecutionResult,
    VerificationResult,
    PresentationDescriptor,
    MemoryCandidate
)
from desktop.models.conversation import NavigationArtifact, NavigationSession, ConversationArtifact

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.execution import ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor


class NavigationCapability(ICapability):
    """
    Navigation Capability (Phase 2).
    Live turn-by-turn guidance consuming a NavigationArtifact.
    """
    def __init__(self):
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "NavigationCapability"

    @property
    def capability_id(self) -> str:
        return "cap_live_navigation"

    @property
    def state(self) -> ServiceState:
        return self._state

    async def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    async def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> dict:
        return {"status": "healthy"}

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(
                name="navigate",
                description="Live turn-by-turn guidance.",
                parameters={}
            )
        ]

    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name == "navigate"

    def cancel(self, invocation_id: str) -> None:
        pass

    async def execute(self, invocation: ToolInvocation, context: 'ExecutionContext') -> ExecutionResult:
        if not self.validate(invocation):
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Invalid tool."])

        # Simulate async execution
        await asyncio.sleep(0)

        payload = invocation.arguments
        artifact: NavigationArtifact = payload.get("active_artifact")
        now = datetime.now()

        # State C: No artifact
        if not artifact or not isinstance(artifact, NavigationArtifact):
            return ExecutionResult(status=ExecutionStatus.SUCCESS, data=self._build_failure_response(
                "Route discovery required. No valid NavigationArtifact provided."
            ))

        # State B: Expired artifact
        if artifact.expires_at and artifact.expires_at < now:
            return ExecutionResult(status=ExecutionStatus.SUCCESS, data=self._build_failure_response(
                "NavigationArtifact expired. Please request a new route.",
                refresh_requested=True
            ))

        # State A: Valid Artifact
        # Initialize mutable session
        session = NavigationSession(
            session_id=str(uuid.uuid4()),
            artifact_id=artifact.artifact_id,
            current_waypoint=1,
            remaining_distance=40.0,
            remaining_eta=40,
            navigation_status="active"
        )

        cap_exec_result = CapExecutionResult(
            success=True,
            payload={
                "session_id": session.session_id,
                "status": session.navigation_status,
                "current_instruction": "In 500 meters, turn right.",
                "remaining_eta": session.remaining_eta
            }
        )

        verify_result = VerificationResult(
            verified=True,
            evidence_ids=["gps_sensor"],
            verification_strategy="location_polling"
        )

        # Navigation artifact remains untouched (immutable), we just emit a generic update
        new_artifact = ConversationArtifact(
            artifact_id=str(uuid.uuid4()),
            artifact_type="NavigationUpdateArtifact",
            capability_id=self.capability_id,
            timestamp=now,
            summary=f"Navigating to {artifact.destination}. ETA {session.remaining_eta} mins.",
            structured_result=cap_exec_result.payload,
            referenced_entities=[],
            supported_followup_actions=["Stop Navigation", "Traffic"],
            presentation_available=True,
            expiration_policy="transient",
            confidence=0.99
        )

        pres_descriptor = PresentationDescriptor(
            experience_id="exp_navigation_live",
            recipe_id="recipe_turn_by_turn",
            layout_data={
                "instruction": "Turn right",
                "eta": f"{session.remaining_eta} mins",
                "destination": artifact.destination
            }
        )

        mem_candidate = MemoryCandidate(
            activity_type="Active Navigation",
            workspace_hint="Live GPS",
            related_entities=[artifact.destination],
            timestamp=now
        )

        canonical_out = CanonicalCapabilityOutput(
            execution_result=cap_exec_result,
            verification_result=verify_result,
            conversation_artifact=new_artifact,
            presentation_descriptor=pres_descriptor,
            memory_candidate=mem_candidate
        )
        return ExecutionResult(status=ExecutionStatus.SUCCESS, data=canonical_out)

    def _build_failure_response(self, message: str, refresh_requested: bool = False) -> CanonicalCapabilityOutput:
        cap_exec_result = CapExecutionResult(
            success=False,
            payload={"refresh_requested": refresh_requested},
            error_message=message
        )
        
        verify_result = VerificationResult(False, [], "none")
        
        artifact = ConversationArtifact(
            artifact_id=str(uuid.uuid4()),
            artifact_type="ErrorArtifact",
            capability_id=self.capability_id,
            timestamp=datetime.now(),
            summary=message,
            structured_result={},
            referenced_entities=[],
            supported_followup_actions=[],
            presentation_available=False,
            expiration_policy="transient",
            confidence=1.0
        )
        
        pres_descriptor = PresentationDescriptor("none", "none", {})
        mem_candidate = MemoryCandidate("Error", "System", [], datetime.now())
        
        return CanonicalCapabilityOutput(cap_exec_result, verify_result, artifact, pres_descriptor, mem_candidate)
