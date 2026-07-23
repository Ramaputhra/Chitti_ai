from abc import ABC, abstractmethod
from typing import Optional
from desktop.models.presentation import PresentationSession, PresentationModel, PresentationPatch
from desktop.platform.core.presentation.transport import IFrontendTransport

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

class BrowserRenderer(IRenderer):
    """
    Primary web-based renderer. Delegates physical network routing to its transport.
    """
    def __init__(self, transport: IFrontendTransport):
        self.transport = transport

    def initialize_session(self, session: PresentationSession) -> bool:
        return self.transport.send_payload(session.session_id, "INIT", {"template": session.template.template_id if session.template else "default"})
        
    def render(self, session_id: str, model: PresentationModel) -> bool:
        return self.transport.send_payload(session_id, "RENDER", {"model_type": model.model_type, "data": model.data})
        
    def patch(self, session_id: str, patch: PresentationPatch) -> bool:
        return self.transport.send_payload(session_id, "PATCH", {"target": patch.target_widget_id, "diff": patch.diff_data})
        
    def focus(self, session_id: str) -> bool:
        return self.transport.send_payload(session_id, "FOCUS", {})
        
    def hide(self, session_id: str) -> bool:
        return self.transport.send_payload(session_id, "HIDE", {})
        
    def show(self, session_id: str) -> bool:
        return self.transport.send_payload(session_id, "SHOW", {})
        
    def close_session(self, session_id: str) -> bool:
        return self.transport.send_payload(session_id, "CLOSE", {})

class ConsoleRenderer(IRenderer):
    """
    CLI fallback renderer for debugging.
    """
    def initialize_session(self, session: PresentationSession) -> bool:
        print(f"\n--- [UI SESSION STARTED: {session.session_id}] ---")
        return True
        
    def render(self, session_id: str, model: PresentationModel) -> bool:
        print(f"[UI RENDER: {model.model_type}] -> {model.data}")
        return True
        
    def patch(self, session_id: str, patch: PresentationPatch) -> bool:
        print(f"[UI PATCH: {patch.target_widget_id}] -> {patch.diff_data}")
        return True
        
    def focus(self, session_id: str) -> bool:
        print(f"[UI FOCUS: {session_id}]")
        return True
        
    def hide(self, session_id: str) -> bool:
        print(f"[UI HIDE: {session_id}]")
        return True
        
    def show(self, session_id: str) -> bool:
        print(f"[UI SHOW: {session_id}]")
        return True
        
    def close_session(self, session_id: str) -> bool:
        print(f"--- [UI SESSION CLOSED: {session_id}] ---\n")
        return True
