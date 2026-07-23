import uuid

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.models.orchestration import AIRequest
from desktop.platform.shared.utilities.prompt_composer import PromptComposer
from desktop.platform.shared.utilities.workspace_context_builder import WorkspaceContextBuilder
from desktop.runtime.orchestration.orchestrator import AIOrchestrator
from desktop.services.capabilities.calendar_capability import CalendarCapability
from desktop.services.capabilities.notes_capability import NotesCapability
from desktop.services.capabilities.documents_capability import DocumentsCapability
from desktop.services.ui.notification_queue import NotificationQueue


class MeetingPreparationWorkflow:
    """
    Workflow P0-006: Prepares the user for their next meeting by gathering
    Calendar, Notes, and Recent Documents context.
    """
    def __init__(
        self,
        logger: ILoggingService,
        orchestrator: AIOrchestrator,
        queue: NotificationQueue,
        calendar_cap: CalendarCapability,
        notes_cap: NotesCapability,
        docs_cap: DocumentsCapability
    ) -> None:
        self.logger = logger
        self.orchestrator = orchestrator
        self.queue = queue
        self.calendar_cap = calendar_cap
        self.notes_cap = notes_cap
        self.docs_cap = docs_cap

    def execute(self) -> None:
        self.logger.info("Starting Meeting Preparation Workflow...")

        # Find the meeting name via Calendar, or simply fetch context
        # For version 0.1, we fetch today's calendar and use "meeting" as the note query
        ctx = WorkspaceContextBuilder.build(
            logger=self.logger,
            calendar_cap=self.calendar_cap,
            notes_cap=self.notes_cap,
            docs_cap=self.docs_cap,
            meeting_query="meeting"
        )

        prompt = PromptComposer.compose_meeting_brief(ctx)

        request = AIRequest(
            id=str(uuid.uuid4()),
            capability="reasoning",
            payload=prompt
        )

        self.logger.info("Sending Meeting Brief Request to AI Orchestrator...")
        response = self.orchestrator.submit_request(request)

        if response and response.status == "success":
            brief_text = response.result
            self.logger.info(f"Generated Meeting Brief: {brief_text}")
            
            # Queue Audio
            self.queue.enqueue(brief_text)
        else:
            self.logger.error("Failed to generate Meeting Brief.")
            self.queue.enqueue("I'm sorry, I was unable to prepare your meeting brief.")
