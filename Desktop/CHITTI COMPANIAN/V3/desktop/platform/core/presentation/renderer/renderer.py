from abc import ABC, abstractmethod
from desktop.models.presentation import PresentationSession, PresentationModel, PresentationPatch

class IRenderer(ABC):
    """
    Abstract interface for all rendering engines (Browser, Console, Mobile, etc).
    """
    @abstractmethod
    def initialize_session(self, session: PresentationSession) -> bool:
        pass
        
    @abstractmethod
    def render(self, session_id: str, model: PresentationModel) -> bool:
        pass
        
    @abstractmethod
    def patch(self, session_id: str, patch: PresentationPatch) -> bool:
        pass
        
    @abstractmethod
    def focus(self, session_id: str) -> bool:
        pass
        
    @abstractmethod
    def hide(self, session_id: str) -> bool:
        pass
        
    @abstractmethod
    def show(self, session_id: str) -> bool:
        pass
        
    @abstractmethod
    def close_session(self, session_id: str) -> bool:
        pass
