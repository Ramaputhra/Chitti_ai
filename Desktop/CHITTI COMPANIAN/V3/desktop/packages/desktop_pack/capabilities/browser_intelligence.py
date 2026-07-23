from typing import List, Dict, Any
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.models.capability import (
    ExecutionResult, CanonicalCapabilityOutput, VerificationResult, 
    PresentationDescriptor, MemoryCandidate
)
from desktop.models.conversation import PageArtifact
from datetime import datetime

def _mock_canonical(payload: Dict[str, Any]) -> CanonicalCapabilityOutput:
    return CanonicalCapabilityOutput(
        execution_result=ExecutionResult(success=True, payload=payload),
        verification_result=VerificationResult(verified=True, evidence_ids=[], verification_strategy="mock"),
        conversation_artifact=PageArtifact(
            artifact_id="mock", artifact_type="PageArtifact", capability_id="mock",
            timestamp=datetime.now(), summary="", structured_result={}, referenced_entities=[],
            supported_followup_actions=[], presentation_available=False, expiration_policy="", confidence=1.0
        ),
        presentation_descriptor=PresentationDescriptor(experience_id="", recipe_id="", layout_data={}),
        memory_candidate=MemoryCandidate(activity_type="", workspace_hint="", related_entities=[])
    )

class BrowserNavigationCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["browser_navigate"]
    def describe(self) -> Dict[str, Any]: return {"name": "BrowserNavigationCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        url = invocation.arguments.get("url", "")
        print(f"[ExecutionRuntime] Automating navigation to: {url}")
        return _mock_canonical({"navigated": url})

class BrowserDOMCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["browser_dom"]
    def describe(self) -> Dict[str, Any]: return {"name": "BrowserDOMCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Scanning raw HTML, stripping CSS/JS, converting to semantic LayoutTree...")
        return _mock_canonical({"layout_tree": "MockLayoutTree"})

class BrowserSearchCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["browser_search"]
    def describe(self) -> Dict[str, Any]: return {"name": "BrowserSearchCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Analyzing SERP LayoutTree. Emitting SearchArtifact.")
        return _mock_canonical({"search_results": True})

class BrowserCommerceCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["browser_commerce"]
    def describe(self) -> Dict[str, Any]: return {"name": "BrowserCommerceCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Analyzing Commerce LayoutTree. Extracting price/stock. Emitting ShoppingArtifact.")
        return _mock_canonical({"commerce_data": True})

class BrowserAuthenticationCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["browser_auth"]
    def describe(self) -> Dict[str, Any]: return {"name": "BrowserAuthenticationCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Scanning LayoutTree for Auth state. Emitting AuthenticationArtifact.")
        return _mock_canonical({"auth_state": "REQUIRES_LOGIN"})

class BrowserFormCapability(ICapability):
    def initialize(self) -> None: pass
    def shutdown(self) -> None: pass
    def discover_tools(self) -> List[str]: return ["browser_form"]
    def describe(self) -> Dict[str, Any]: return {"name": "BrowserFormCapability", "version": "1.0"}
    def validate(self, invocation: ToolInvocation) -> bool: return invocation.tool_name in self.discover_tools()
    def execute(self, invocation: ToolInvocation) -> CanonicalCapabilityOutput:
        print("[ExecutionRuntime] Extracting interactive form fields from LayoutTree.")
        return _mock_canonical({"form_schema": True})
