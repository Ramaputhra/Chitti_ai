from typing import List

try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import ToolInvocation
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.runtimes.presentation.models import PresentationModel, PresentationType, PresentationMetadata, PresentationCapability, PresentationLifetime
from desktop.runtimes.world.world_runtime import WorldRuntime

class ClipboardCapability(ICapability):
    """Provides explicit read/write access to the system clipboard. Follows Rule 52 and Rule 105."""
    
    def __init__(self, world_runtime: WorldRuntime):
        self.world_runtime = world_runtime
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "ClipboardCapability"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def health_check(self) -> dict:
        return {"status": "healthy" if HAS_PYPERCLIP else "degraded (missing pyperclip)"}

    def describe(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            name="clipboard",
            version="2.0",
            category="desktop",
            permissions=["clipboard"],
            tools=self.discover_tools(),
            health="healthy" if HAS_PYPERCLIP else "degraded",
            platform="all"
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(name="read_clipboard", description="Read the current text from the system clipboard. Do NOT call this unless the user explicitly asks.", parameters=[]),
            ToolDescriptor(
                name="write_clipboard", 
                description="Write text to the system clipboard.", 
                parameters=[ToolParameter(name="text", type="string", description="The text to write.", required=True)]
            )
        ]

    def validate(self, invocation: ToolInvocation) -> bool:
        if invocation.tool_name == "read_clipboard":
            return True
        elif invocation.tool_name == "write_clipboard":
            return "text" in invocation.parameters
        return False

    def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        if not self.validate(invocation):
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Invalid tool."])

        if not HAS_PYPERCLIP and invocation.tool_name == "write_clipboard":
            return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["pyperclip library is required to write to clipboard."])

        if invocation.tool_name == "read_clipboard":
            # Rule 105: Do not query OS directly. Read from WorldSnapshot.
            snapshot = self.world_runtime.get_current_snapshot()
            content = snapshot.clipboard if snapshot.clipboard is not None else ""
            summary = "Read from clipboard"
            
            model = PresentationModel(
                type=PresentationType.TIMELINE,
                title="Clipboard Activity",
                subtitle="Read Operation",
                icon="clipboard-outline",
                data={"content": content, "action": "read"},
                actions=[],
                metadata=PresentationMetadata(
                    capabilities=[PresentationCapability.COPY],
                    lifetime=PresentationLifetime.TRANSIENT
                )
            )
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=summary, presentation=model)
            
        elif invocation.tool_name == "write_clipboard":
            text = invocation.parameters["text"]
            pyperclip.copy(text)
            summary = "Copied to clipboard"
            
            model = PresentationModel(
                type=PresentationType.TIMELINE,
                title="Clipboard Activity",
                subtitle="Write Operation",
                icon="clipboard-check",
                data={"content": text, "action": "write"},
                actions=[],
                metadata=PresentationMetadata(
                    capabilities=[],
                    lifetime=PresentationLifetime.TRANSIENT
                )
            )
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=summary, presentation=model)

        return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Execution failed"])

    def cancel(self, invocation_id: str) -> None:
        pass
