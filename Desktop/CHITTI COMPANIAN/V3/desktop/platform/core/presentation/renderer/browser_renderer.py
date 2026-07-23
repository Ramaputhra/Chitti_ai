from desktop.models.presentation import PresentationSession, PresentationModel, PresentationPatch
from desktop.platform.core.presentation.renderer.renderer import IRenderer
from desktop.platform.core.presentation.transport.base import IFrontendTransport
from desktop.platform.core.presentation.protocol.serializer import ProtocolSerializer
from desktop.models.presentation import (
    RenderCommand, PatchCommand, FocusCommand, CloseCommand
)

class BrowserRenderer(IRenderer):
    """
    Primary web-based renderer. Delegates physical network routing to its transport.
    Uses ProtocolSerializer to format messages (Rule 320/321).
    """
    def __init__(self, transport: IFrontendTransport, serializer: ProtocolSerializer):
        self.transport = transport
        self.serializer = serializer

    def initialize_session(self, session: PresentationSession) -> bool:
        # Instead of directly sending JSON dicts, we would create a Handshake/Init command here.
        # But for now, we leave this as a stub that will be fleshed out with specific protocol commands.
        return True
        
    def render(self, session_id: str, model: PresentationModel) -> bool:
        # In a real setup, PresentationRuntime passes the serialized command through.
        # If the renderer itself is called, it would use the serializer:
        cmd = RenderCommand(command_id="stub", session_id=session_id, model_version=1, model=model)
        envelope = self.serializer.serialize_command(cmd)
        return self.transport.send_message(envelope.__dict__)
        
    def patch(self, session_id: str, patch: PresentationPatch) -> bool:
        cmd = PatchCommand(command_id="stub", session_id=session_id, model_version=1, patch=patch)
        envelope = self.serializer.serialize_command(cmd)
        return self.transport.send_message(envelope.__dict__)
        
    def focus(self, session_id: str) -> bool:
        cmd = FocusCommand(command_id="stub", session_id=session_id, model_version=1)
        envelope = self.serializer.serialize_command(cmd)
        return self.transport.send_message(envelope.__dict__)
        
    def hide(self, session_id: str) -> bool:
        return True
        
    def show(self, session_id: str) -> bool:
        return True
        
    def close_session(self, session_id: str) -> bool:
        cmd = CloseCommand(command_id="stub", session_id=session_id, model_version=1)
        envelope = self.serializer.serialize_command(cmd)
        return self.transport.send_message(envelope.__dict__)
