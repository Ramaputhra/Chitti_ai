import uuid
import time
from typing import Any
from desktop.platform.core.presentation.protocol.messages import (
    FrontendProtocolMessage, MessageDirection
)
from desktop.models.presentation import (
    PresentationCommand, FrontendEvent
)

class ProtocolSerializer:
    """
    Serializes and deserializes internal domain models to and from the FrontendProtocolMessage envelope.
    Protects the internal Presentation models from leaking directly to the wire.
    """
    PROTOCOL_VERSION = 1

    def serialize_command(self, command: PresentationCommand) -> FrontendProtocolMessage:
        """
        Converts an internal PresentationCommand (from the command queue) into a stable wire envelope.
        """
        payload = {}
        # In a real implementation, we would deeply serialize the dataclass here using marshmallow or similar.
        # Stubbing generic dictionary conversion for the architecture prototype.
        if hasattr(command, "__dict__"):
            payload = command.__dict__.copy()
            # Clean up non-serializable fields if needed

        return FrontendProtocolMessage(
            protocol_version=self.PROTOCOL_VERSION,
            message_id=f"msg_{uuid.uuid4().hex[:10]}",
            correlation_id=command.command_id,
            timestamp=time.time(),
            direction=MessageDirection.BACKEND_TO_FRONTEND,
            message_type=command.__class__.__name__,
            session_id=command.session_id,
            payload=payload
        )

    def deserialize_event(self, envelope: dict) -> FrontendEvent:
        """
        Converts an incoming JSON dictionary (matching FrontendProtocolMessage) into an internal FrontendEvent.
        """
        # Validate protocol version
        if envelope.get("protocol_version", 0) != self.PROTOCOL_VERSION:
            raise ValueError(f"Unsupported protocol version: {envelope.get('protocol_version')}")
            
        message_type = envelope.get("message_type")
        payload = envelope.get("payload", {})
        session_id = envelope.get("session_id")
        
        # Stub: instantiate the appropriate internal FrontendEvent dataclass.
        # In a robust implementation, this would use a registry of known event types.
        event_class = globals().get(message_type, FrontendEvent)
        return event_class(session_id=session_id, timestamp=time.time(), **payload)
