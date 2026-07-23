import asyncio
from typing import List, Dict, Any
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.tool import ToolDescriptor
from desktop.platform.shared.models.execution import ExecutionResult, ExecutionStatus
from desktop.models.capability import (
    ExecutionResult as CapExecutionResult, CanonicalCapabilityOutput, VerificationResult, 
    PresentationDescriptor, MemoryCandidate
)
from desktop.models.conversation import PageArtifact
from datetime import datetime

def _mock_canonical(payload: Dict[str, Any]) -> CanonicalCapabilityOutput:
    return CanonicalCapabilityOutput(
        execution_result=CapExecutionResult(success=True, payload=payload),
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
    def __init__(self):
        self._state = ServiceState.STOPPED
    
    @property
    def name(self) -> str:
        return "BrowserNavigationCapability"
    
    @property
    def capability_id(self) -> str:
        return "browser_navigation"
    
    async def initialize(self) -> None:
        self._state = ServiceState.RUNNING
    
    async def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
    
    def discover_tools(self) -> List[ToolDescriptor]:
        return [ToolDescriptor(name="browser_navigate", description="Navigate to URL", parameters={})]
    
    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name in ["browser_navigate"]
    
    async def execute(self, invocation: ToolInvocation, context: Any) -> ExecutionResult:
        await asyncio.sleep(0)
        url = invocation.arguments.get("url", "")
        print(f"[ExecutionRuntime] Automating navigation to: {url}")
        return ExecutionResult(status=ExecutionStatus.SUCCESS, data=_mock_canonical({"navigated": url}))

class BrowserDOMCapability(ICapability):
    def __init__(self):
        self._state = ServiceState.STOPPED
    
    @property
    def name(self) -> str:
        return "BrowserDOMCapability"
    
    @property
    def capability_id(self) -> str:
        return "browser_dom"
    
    async def initialize(self) -> None:
        self._state = ServiceState.RUNNING
    
    async def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
    
    def discover_tools(self) -> List[ToolDescriptor]:
        return [ToolDescriptor(name="browser_dom", description="Get DOM structure", parameters={})]
    
    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name in ["browser_dom"]
    
    async def execute(self, invocation: ToolInvocation, context: Any) -> ExecutionResult:
        await asyncio.sleep(0)
        print("[ExecutionRuntime] Scanning raw HTML, stripping CSS/JS, converting to semantic LayoutTree...")
        return ExecutionResult(status=ExecutionStatus.SUCCESS, data=_mock_canonical({"layout_tree": "MockLayoutTree"}))

class BrowserSearchCapability(ICapability):
    def __init__(self):
        self._state = ServiceState.STOPPED
    
    @property
    def name(self) -> str:
        return "BrowserSearchCapability"
    
    @property
    def capability_id(self) -> str:
        return "browser_search"
    
    async def initialize(self) -> None:
        self._state = ServiceState.RUNNING
    
    async def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
    
    def discover_tools(self) -> List[ToolDescriptor]:
        return [ToolDescriptor(name="browser_search", description="Search the web", parameters={})]
    
    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name in ["browser_search"]
    
    async def execute(self, invocation: ToolInvocation, context: Any) -> ExecutionResult:
        await asyncio.sleep(0)
        print("[ExecutionRuntime] Analyzing SERP LayoutTree. Emitting SearchArtifact.")
        return ExecutionResult(status=ExecutionStatus.SUCCESS, data=_mock_canonical({"search_results": True}))

class BrowserCommerceCapability(ICapability):
    def __init__(self):
        self._state = ServiceState.STOPPED
    
    @property
    def name(self) -> str:
        return "BrowserCommerceCapability"
    
    @property
    def capability_id(self) -> str:
        return "browser_commerce"
    
    async def initialize(self) -> None:
        self._state = ServiceState.RUNNING
    
    async def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
    
    def discover_tools(self) -> List[ToolDescriptor]:
        return [ToolDescriptor(name="browser_commerce", description="Extract commerce data", parameters={})]
    
    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name in ["browser_commerce"]
    
    async def execute(self, invocation: ToolInvocation, context: Any) -> ExecutionResult:
        await asyncio.sleep(0)
        print("[ExecutionRuntime] Analyzing Commerce LayoutTree. Extracting price/stock. Emitting ShoppingArtifact.")
        return ExecutionResult(status=ExecutionStatus.SUCCESS, data=_mock_canonical({"commerce_data": True}))

class BrowserAuthenticationCapability(ICapability):
    def __init__(self):
        self._state = ServiceState.STOPPED
    
    @property
    def name(self) -> str:
        return "BrowserAuthenticationCapability"
    
    @property
    def capability_id(self) -> str:
        return "browser_auth"
    
    async def initialize(self) -> None:
        self._state = ServiceState.RUNNING
    
    async def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
    
    def discover_tools(self) -> List[ToolDescriptor]:
        return [ToolDescriptor(name="browser_auth", description="Check auth state", parameters={})]
    
    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name in ["browser_auth"]
    
    async def execute(self, invocation: ToolInvocation, context: Any) -> ExecutionResult:
        await asyncio.sleep(0)
        print("[ExecutionRuntime] Scanning LayoutTree for Auth state. Emitting AuthenticationArtifact.")
        return ExecutionResult(status=ExecutionStatus.SUCCESS, data=_mock_canonical({"auth_state": "REQUIRES_LOGIN"}))

class BrowserFormCapability(ICapability):
    def __init__(self):
        self._state = ServiceState.STOPPED
    
    @property
    def name(self) -> str:
        return "BrowserFormCapability"
    
    @property
    def capability_id(self) -> str:
        return "browser_form"
    
    async def initialize(self) -> None:
        self._state = ServiceState.RUNNING
    
    async def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
    
    def discover_tools(self) -> List[ToolDescriptor]:
        return [ToolDescriptor(name="browser_form", description="Extract form fields", parameters={})]
    
    def validate(self, invocation: ToolInvocation) -> bool:
        return invocation.tool_name in ["browser_form"]
    
    async def execute(self, invocation: ToolInvocation, context: Any) -> ExecutionResult:
        await asyncio.sleep(0)
        print("[ExecutionRuntime] Extracting interactive form fields from LayoutTree.")
        return ExecutionResult(status=ExecutionStatus.SUCCESS, data=_mock_canonical({"form_schema": True}))
