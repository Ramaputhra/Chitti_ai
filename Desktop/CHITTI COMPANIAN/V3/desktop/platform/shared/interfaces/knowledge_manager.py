from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.session import ConversationSession


class IKnowledgeManager(IService):
    """
    The absolute gateway to the Knowledge Graph Runtime.
    Nothing bypasses this layer to access knowledge or artifacts.
    """
    def process_session(self, session: ConversationSession) -> None:
        ...
