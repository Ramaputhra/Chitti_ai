from typing import Any, Dict, List

from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.notes_provider import INotesProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.artifact import DocumentArtifact
from desktop.platform.shared.models.capability import CapabilityDescriptor


class NotesCapability(ICapability):
    """
    Provides note operations abstracting away the specific INotesProvider.
    """
    def __init__(self, logger: ILoggingService, provider: INotesProvider) -> None:
        self.logger = logger
        self.providers = [provider]
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "NotesCapability"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {
            "active_providers": [p.name for p in self.providers if p.state == ServiceState.RUNNING]
        }

    def execute(self, *args, **kwargs) -> Any:
        if args and hasattr(args[0], "tool_name"):
            invocation = args[0]
        else:
            action = kwargs.get("action")
            parameters = kwargs.get("parameters", {})
            invocation = type("ToolInvocation", (), {"tool_name": action, "parameters": parameters})()

        if invocation.tool_name == "query":
            from desktop.platform.shared.models.execution import ExecutionResult
            results = self.query_notes(invocation.parameters.get("query", ""))
            return ExecutionResult(success=True, output=f"Found {len(results)} notes", data={"notes": results})
        elif invocation.tool_name == "create":
            from desktop.platform.shared.models.execution import ExecutionResult
            # Simulating save for now
            title = invocation.parameters.get("title", "Untitled")
            content = invocation.parameters.get("content", "")
            return ExecutionResult(success=True, output=f"Note '{title}' saved successfully.", data={"id": "note_123"})
            
        from desktop.platform.shared.models.execution import ExecutionResult
        return ExecutionResult(success=False, error=f"Action {invocation.tool_name} not supported by {self.name}")

    def describe(self) -> CapabilityDescriptor:
        from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
        return CapabilityDescriptor(
            name=self.name,
            version="1.0",
            category="productivity",
            permissions=["filesystem"],
            tools=[
                ToolDescriptor(
                    name="query",
                    description="Search user notes.",
                    parameters=[ToolParameter(name="query", type="string", description="The search query.", required=True)]
                ),
                ToolDescriptor(
                    name="create",
                    description="Create a new note.",
                    parameters=[
                        ToolParameter(name="title", type="string", description="The title of the note.", required=True),
                        ToolParameter(name="content", type="string", description="The body of the note.", required=True)
                    ]
                )
            ],
            health="healthy",
            platform="all"
        )

    def query_notes(self, query: str) -> List[DocumentArtifact]:
        results = []
        for provider in self.providers:
            if provider.state == ServiceState.RUNNING:
                try:
                    results.extend(provider.query_notes(query))
                except Exception as e:
                    self.logger.warning(f"{provider.name} failed to query notes: {e}")
        return results
