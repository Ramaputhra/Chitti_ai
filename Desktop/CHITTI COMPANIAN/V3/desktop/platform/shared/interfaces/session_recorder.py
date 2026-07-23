from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.session import ConversationSession


class ISessionRecorder(IService):
    """
    Saves closed ConversationSessions to disk for analytics and history.
    """
    def save_session(self, session: ConversationSession) -> str:
        ...
