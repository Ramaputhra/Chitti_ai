from desktop.models.presentation import PresentationSession, PresentationModel, PresentationPatch
from desktop.platform.core.presentation.renderer.renderer import IRenderer

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
