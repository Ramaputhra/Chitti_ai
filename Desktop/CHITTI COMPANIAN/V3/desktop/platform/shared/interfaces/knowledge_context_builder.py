from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.session import ConversationSession


class IKnowledgeContextBuilder(IService):
    """
    Selects the right knowledge using the RetrievalEngine and formats it for the LLM prompt.
    Sits between the Conversation and the Retrieval layers.
    """
    def build_context(self, session: ConversationSession) -> str:
        ...
