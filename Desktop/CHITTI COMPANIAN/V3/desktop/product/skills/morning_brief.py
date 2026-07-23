import uuid
import concurrent.futures
from typing import Any, Dict, List

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.models.artifact import Artifact
from desktop.platform.shared.models.orchestration import AIRequest
from desktop.platform.shared.utilities.prompt_composer import PromptComposer
from desktop.platform.shared.utilities.workspace_context_builder import WorkspaceContextBuilder
from desktop.runtime.orchestration.orchestrator import AIOrchestrator
from desktop.services.capabilities.calendar_capability import CalendarCapability
from desktop.services.capabilities.mail_capability import MailCapability
from desktop.services.capabilities.desktop_context_capability import DesktopContextCapability
from desktop.services.ui.notification_queue import NotificationQueue


class MorningBriefWorkflow:
    """
    Executes the Morning Brief sequence:
    1. Gathers Desktop Context.
    2. Gathers Calendar events.
    3. Gathers Unread Mail.
    4. Passes structured artifacts to AIOrchestrator for summarization.
    5. Reads the result via TTS.
    """
    def __init__(
        self,
        logger: ILoggingService,
        orchestrator: AIOrchestrator,
        queue: NotificationQueue,
        calendar_cap: CalendarCapability,
        mail_cap: MailCapability,
        context_cap: DesktopContextCapability
    ) -> None:
        self.logger = logger
        self.orchestrator = orchestrator
        self.queue = queue
        self.calendar_cap = calendar_cap
        self.mail_cap = mail_cap
        self.context_cap = context_cap

    def execute(self) -> None:
        self.logger.info("Starting Morning Brief Workflow...")

        ctx = WorkspaceContextBuilder.build(
            logger=self.logger,
            calendar_cap=self.calendar_cap,
            mail_cap=self.mail_cap,
            context_cap=self.context_cap
        )

        prompt = PromptComposer.compose_morning_brief(ctx)

        request = AIRequest(
            id=str(uuid.uuid4()),
            capability="reasoning",
            payload=prompt
        )

        self.logger.info("Dispatching Morning Brief to AI Orchestrator...")
        response = self.orchestrator.submit_request(request)

        if response and response.status == "success":
            brief_text = response.result
            self.logger.info(f"Generated Brief: {brief_text}")
            
            # 5. Queue Audio
            self.queue.enqueue(brief_text)
        else:
            self.logger.error("Failed to generate Morning Brief.")
            self.queue.enqueue("I'm sorry, I was unable to generate your morning brief.")
