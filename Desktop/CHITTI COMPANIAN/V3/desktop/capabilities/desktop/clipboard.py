from typing import List, Optional, Dict, Any

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

class ClipboardCapability(ICapability):
    """Provides explicit read/write access to the system clipboard. Follows Rule 52 and Rule 105."""
    
    def __init__(self):
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
            id="clipboard",
            version="2.0",
            permissions=["clipboard"],
            execution_mode="sync",
            factory=None
        )

    def discover_tools(self) -> List[ToolDescriptor]:
        return [
            ToolDescriptor(name="read_clipboard", description="Read the current text from the system clipboard.", parameters=[]),
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
            content = ""
            if HAS_PYPERCLIP:
                try:
                    content = pyperclip.paste()
                except Exception:
                    pass
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output_data={"content": content}
            )
            
        elif invocation.tool_name == "write_clipboard":
            text = invocation.parameters.get("text", "")
            if HAS_PYPERCLIP:
                try:
                    pyperclip.copy(text)
                except Exception as e:
                    return ExecutionResult(status=ExecutionStatus.FAILURE, errors=[str(e)])
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output_data={"written": text}
            )

        return ExecutionResult(status=ExecutionStatus.FAILURE, errors=["Unknown tool"])

    def cancel(self, invocation_id: str) -> None:
        pass
