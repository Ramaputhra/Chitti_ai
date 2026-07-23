from typing import List, Dict, Any
from datetime import datetime
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.models.capability import (
    ExecutionResult, CanonicalCapabilityOutput, VerificationResult, 
    PresentationDescriptor, MemoryCandidate
)
from desktop.models.activity import ActivityArtifact, WorkflowArtifact, TaskArtifact, ProgressArtifact

def _mock_canonical(payload: Dict[str, Any], artifact_instance: Any = None) -> CanonicalCapabilityOutput:
    return CanonicalCapabilityOutput(
        execution_result=ExecutionResult(success=True, payload=payload),
        verification_result=VerificationResult(verified=True, evidence_ids=[], verification_strategy="mock_activity"),
        conversation_artifact=artifact_instance,
        presentation_descriptor=PresentationDescriptor(experience_id="activity_exp", recipe_id="recipe_activity_dashboard", layout_data={}),
        memory_candidate=MemoryCandidate(activity_type="Activity Check", workspace_hint="ContextWorkspace", related_entities=[])
    )

class ActivityDetectionCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["activity_detect"]
    def describe(self) -> Dict[str, Any]: return {"name": "ActivityDetectionCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Analyzing BrowserWorkspaceSummary and VisionWorkspaceSummary...")
        print("[ExecutionRuntime] Synthesizing high-level behavior. Emitting ActivityArtifact.")
        art = ActivityArtifact(
            artifact_id="act_001", artifact_type="ActivityArtifact", capability_id="ActivityDetectionCapability",
            timestamp=datetime.now(), summary="User is Coding", structured_result={}, referenced_entities=[],
            activity_type="Coding", supporting_artifacts=["browser_123", "vision_456"], confidence=0.95, focus_application="VS Code"
        )
        return _mock_canonical({"detected": True}, artifact_instance=art)

class ActivityContextCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["activity_context"]
    def describe(self) -> Dict[str, Any]: return {"name": "ActivityContextCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Binding disparate semantic artifacts into WorkflowArtifact.")
        art = WorkflowArtifact(
            artifact_id="work_001", artifact_type="WorkflowArtifact", capability_id="ActivityContextCapability",
            timestamp=datetime.now(), summary="Monthly Reporting", structured_result={}, referenced_entities=[],
            activity_type="Reporting", supporting_artifacts=[], confidence=0.90, focus_application="Excel",
            workflow_name="Monthly Expense Reporting", cross_app_context=True, active_participants=["Excel", "Chrome"]
        )
        return _mock_canonical({"workflow": True}, artifact_instance=art)

class ActivityProgressCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["activity_progress"]
    def describe(self) -> Dict[str, Any]: return {"name": "ActivityProgressCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Evaluating historical momentum. Emitting ProgressArtifact.")
        art = ProgressArtifact(
            artifact_id="prog_001", artifact_type="ProgressArtifact", capability_id="ActivityProgressCapability",
            timestamp=datetime.now(), summary="Task Stalled", structured_result={}, referenced_entities=[],
            activity_type="Coding", supporting_artifacts=[], confidence=0.85, focus_application="VS Code",
            momentum_state="STALLED", completion_estimate="Blocked", blockers=["CORS Error"]
        )
        return _mock_canonical({"progress": True}, artifact_instance=art)

class ActivityRecommendationCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["activity_recommend"]
    def describe(self) -> Dict[str, Any]: return {"name": "ActivityRecommendationCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Synthesizing next logical action. Emitting Presentation Overlay.")
        # Does not emit a new artifact, just returns the presentation descriptor
        return _mock_canonical({"recommendation": "Open StackOverflow"})
