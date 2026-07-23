from typing import Optional
from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.session import ConversationSession

class IConversationManager(IService):
    """
    Manages the lifecycle of a ConversationSession, mapping events into the active
    session object and guaranteeing only one session is active at a time.
    Every externally observable interaction (Voice, Desktop, Robot) MUST execute 
    inside a ConversationSession.
    """
    def get_current_session(self) -> Optional[ConversationSession]:
        ...
