from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.models.capability import (
    ExecutionResult,
    VerificationResult,
    PresentationDescriptor,
    MemoryCandidate,
    CanonicalCapabilityOutput
)
from desktop.models.conversation import ConversationArtifact

@dataclass(frozen=True)
class ComponentConfidence:
    workspace: float = 0.0
    applications: float = 0.0
    browser: float = 0.0
    terminal: float = 0.0
    files: float = 0.0
    notes: float = 0.0

@dataclass(frozen=True)
class WorkspaceRestoreSummary:
    workspace_name: str
    last_active_time: datetime
    applications: List[str]
    browser_tabs: List[str]
    files: List[str]
    confidence_scores: ComponentConfidence
    explanation_summary: str

@dataclass(frozen=True)
class WorkspaceRestorePlan:
    workspace_name: str
    last_active_time: datetime
    projects: List[str]
    working_directories: List[str]
    applications: List[str]
    browser_sessions: List[str]
    browser_tabs: List[str]
    files: List[str]
    notes: List[str]
    confidence_scores: ComponentConfidence
    verification_targets: List[str]
    recommended_restore_order: List[str]
    
    def to_summary(self) -> WorkspaceRestoreSummary:
        return WorkspaceRestoreSummary(
            workspace_name=self.workspace_name,
            last_active_time=self.last_active_time,
            applications=self.applications,
            browser_tabs=self.browser_tabs,
            files=self.files,
            confidence_scores=self.confidence_scores,
            explanation_summary=f"Workspace '{self.workspace_name}' containing {len(self.applications)} apps and {len(self.browser_tabs)} tabs."
        )

@dataclass
class ResumeWorkArtifact(ConversationArtifact):
    restore_plan: Optional[WorkspaceRestorePlan] = None

class ResumeWorkCapability(ICapability):
    @property
    def state(self) -> str:
        return "IDLE"

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def discover_tools(self) -> List[str]:
        return ["resume_activity"]

    def describe(self) -> Dict[str, Any]:
        return {
            "name": "ResumeWorkCapability",
            "version": "1.0",
            "tools": self.discover_tools(),
            "description": "Pure planning capability to orchestrate the resumption of a previous workspace from memory."
        }

    def validate(self, invocation: ToolInvocation) -> bool:
        if invocation.tool_name not in self.discover_tools():
            return False
        return True

    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        # 1. Query MemoryRuntime (Mocked abstraction for the V1 execution spine test)
        # In reality, this would query the memory service via context injection.
        # We mock a high-confidence AI Development workspace scenario here to prove the architecture.
        target_project = invocation.arguments.get("project_name", "AI Development")
        
        # 2. Build Component-Level Confidence
        confidence = ComponentConfidence(
            workspace=0.95,
            applications=0.9,
            browser=0.99,
            terminal=1.0,
            files=0.85,
            notes=0.0
        )
        
        # 3. Build Deterministic WorkspaceRestorePlan (Immutable Declarative Object)
        plan = WorkspaceRestorePlan(
            workspace_name=target_project,
            last_active_time=datetime.now(),
            projects=[target_project],
            working_directories=[f"/home/user/projects/{target_project.lower().replace(' ', '_')}"],
            applications=["Cursor", "PowerShell", "Chrome"],
            browser_sessions=["default"],
            browser_tabs=["github.com", "localhost:3000", "docs.python.org"],
            files=["main.py", "README.md"],
            notes=[],
            confidence_scores=confidence,
            verification_targets=["Cursor", "PowerShell", "Chrome"],
            recommended_restore_order=["Chrome", "PowerShell", "Cursor"]
        )
        
        # 4. Produce Execution Result wrapping the plan payload
        execution_result = ExecutionResult(
            success=True,
            payload={"restore_plan": plan.__dict__}
        )
        
        # 5. Produce ConversationArtifact (Narration)
        narration = f"I found your {target_project} workspace from earlier. Everything looks recoverable with high confidence. Would you like to restore everything?"
        artifact = ResumeWorkArtifact(
            artifact_id=f"resumework_{datetime.now().timestamp()}",
            artifact_type="ResumeWork",
            capability_id="ResumeWorkCapability",
            timestamp=datetime.now(),
            summary="Computed workspace restoration plan.",
            structured_result=execution_result.payload,
            referenced_entities=[target_project, "Cursor", "Chrome", "PowerShell"],
            supported_followup_actions=["[Restore All]", "[Restore Selected]", "[View Details]", "[Explain Workspace]", "[Cancel]"],
            presentation_available=True,
            expiration_policy="NEVER",
            confidence=confidence.workspace,
            restore_plan=plan
        )
        
        # 6. Produce PresentationDescriptor
        presentation = PresentationDescriptor(
            experience_id="exp_resume_work",
            recipe_id="recipe_project_dashboard",
            layout_data={
                "workspace_name": plan.workspace_name,
                "confidence_scores": plan.confidence_scores.__dict__,
                "applications": plan.applications,
                "browser_tabs": plan.browser_tabs,
                "files": plan.files,
                "notes": plan.notes,
                "actions": artifact.supported_followup_actions
            }
        )
        
        # 7. Produce VerificationResult (State Comparison Target)
        verification = VerificationResult(
            verified=True,
            evidence_ids=plan.verification_targets,
            verification_strategy="WorkspaceStateComparison"
        )
        
        # 8. Produce MemoryCandidate
        memory = MemoryCandidate(
            activity_type="Workspace Planning",
            workspace_hint="Resume Activity",
            related_entities=[plan.workspace_name]
        )
        
        return CanonicalCapabilityOutput(
            execution_result=execution_result,
            verification_result=verification,
            conversation_artifact=artifact,
            presentation_descriptor=presentation,
            memory_candidate=memory
        )
