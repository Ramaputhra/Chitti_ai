from typing import List

from desktop.platform.shared.interfaces.event_bus import IEventBus
from desktop.platform.shared.interfaces.skill import ISkill
from desktop.platform.shared.models.intent import Intent
from desktop.product.skills.email_assistant import EmailAssistantWorkflow


class EmailSkill(ISkill):
    """
    Skill for handling Email intents using the EmailAssistantWorkflow.
    """
    def __init__(self, event_bus: IEventBus, workflow: EmailAssistantWorkflow) -> None:
        self.event_bus = event_bus
        self.workflow = workflow

    def name(self) -> str:
        return "EmailSkill"

    def description(self) -> str:
        return "Handles reading, summarizing, drafting, and archiving emails."

    def supported_intents(self) -> List[str]:
        return ["EmailIntent"]

    def execute(self, intent: Intent) -> None:
        # The original text was packed into the intent or we can pull it from context
        # For our simple milestone, the text is needed to route to the sub-action
        # The caller (ActionPlanner) should probably pass original_text, but we can also
        # get it if it's attached to the intent. Let's assume intent has original_text.
        text = getattr(intent, 'original_text', '')
        self.workflow.execute(text)
