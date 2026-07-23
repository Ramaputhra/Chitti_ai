from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.ai import ConversationContext


class IContextBuilder(IService):
    """
    Gathers application state, conversation history, memory, and environment
    variables to form a unified, immutable ConversationContext snapshot.
    """
    def build_context(self) -> ConversationContext:
        ...
