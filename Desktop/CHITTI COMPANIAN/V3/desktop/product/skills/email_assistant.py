import uuid
from typing import Any, Dict, List

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.models.artifact import Artifact
from desktop.platform.shared.models.orchestration import AIRequest
from desktop.platform.shared.utilities.prompt_composer import PromptComposer
from desktop.runtime.orchestration.orchestrator import AIOrchestrator
from desktop.services.capabilities.mail_capability import MailCapability
from desktop.services.ui.notification_queue import NotificationQueue


class EmailAction:
    def execute(self, text: str, mail_cap: MailCapability, orchestrator: AIOrchestrator, queue: NotificationQueue, logger: ILoggingService) -> None:
        pass


class SummarizeAction(EmailAction):
    def execute(self, text: str, mail_cap: MailCapability, orchestrator: AIOrchestrator, queue: NotificationQueue, logger: ILoggingService) -> None:
        logger.info("Executing SummarizeAction...")
        try:
            artifacts = mail_cap.execute("query", {"query": "is:unread"})
            if not artifacts:
                queue.enqueue("You have no unread emails.")
                return

            prompt = PromptComposer.compose_email_summary(artifacts)
            
            # Action Suggestions are appended to the LLM instruction inside compose_email_summary
            # so the LLM outputs them naturally.
            
            request = AIRequest(id=str(uuid.uuid4()), capability="reasoning", payload=prompt)
            response = orchestrator.submit_request(request)

            if response and response.status == "success":
                queue.enqueue(response.result)
            else:
                queue.enqueue("I couldn't summarize your emails right now.")
        except Exception as e:
            logger.warning(f"Mail provider unavailable: {e}")
            queue.enqueue("I couldn't reach your mail provider, but your local workspace is ready.")


class ReadAction(EmailAction):
    def execute(self, text: str, mail_cap: MailCapability, orchestrator: AIOrchestrator, queue: NotificationQueue, logger: ILoggingService) -> None:
        logger.info("Executing ReadAction...")
        try:
            artifacts = mail_cap.execute("query", {"query": "is:unread"})
            if not artifacts:
                queue.enqueue("You have no unread emails.")
                return
            count = len(artifacts)
            queue.enqueue(f"You have {count} unread emails.")
        except Exception as e:
            logger.warning(f"Mail provider unavailable: {e}")
            queue.enqueue("I couldn't reach your mail provider, but your local workspace is ready.")


class DraftAction(EmailAction):
    def execute(self, text: str, mail_cap: MailCapability, orchestrator: AIOrchestrator, queue: NotificationQueue, logger: ILoggingService) -> None:
        logger.info("Executing DraftAction...")
        queue.enqueue("Drafting replies is not fully implemented yet, but I have noted your intent.")


class ArchiveAction(EmailAction):
    def execute(self, text: str, mail_cap: MailCapability, orchestrator: AIOrchestrator, queue: NotificationQueue, logger: ILoggingService) -> None:
        logger.info("Executing ArchiveAction...")
        queue.enqueue("Archiving specific emails is not fully implemented yet, but I have noted your intent.")


class EmailAssistantWorkflow:
    """
    Orchestrates email-related intents by routing to specific Actions.
    """
    def __init__(
        self,
        logger: ILoggingService,
        orchestrator: AIOrchestrator,
        queue: NotificationQueue,
        mail_cap: MailCapability
    ) -> None:
        self.logger = logger
        self.orchestrator = orchestrator
        self.queue = queue
        self.mail_cap = mail_cap
        
        self.actions = {
            "summarize": SummarizeAction(),
            "read": ReadAction(),
            "draft": DraftAction(),
            "archive": ArchiveAction(),
        }

    def execute(self, text: str) -> None:
        self.logger.info(f"EmailAssistantWorkflow received text: {text}")
        
        # Super simple rule-based routing to actions
        text_lower = text.lower()
        if "summarize" in text_lower or "important" in text_lower:
            action = self.actions["summarize"]
        elif "draft" in text_lower or "reply" in text_lower:
            action = self.actions["draft"]
        elif "archive" in text_lower:
            action = self.actions["archive"]
        else:
            action = self.actions["read"]

        action.execute(text, self.mail_cap, self.orchestrator, self.queue, self.logger)
