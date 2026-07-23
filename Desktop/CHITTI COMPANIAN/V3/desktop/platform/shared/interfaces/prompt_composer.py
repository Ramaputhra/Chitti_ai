from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.ai import ConversationContext, Prompt


class IPromptComposer(IService):
    """
    Transforms the unified ConversationContext and user message into
    a strictly-ordered Prompt object for LLM inference.
    """
    def compose(self, context: ConversationContext, user_message: str) -> Prompt:
        ...
