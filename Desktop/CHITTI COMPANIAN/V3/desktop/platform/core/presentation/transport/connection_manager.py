import logging
from typing import Dict, Any
from desktop.platform.core.presentation.transport.base import IFrontendTransport
from desktop.platform.core.presentation.protocol.serializer import ProtocolSerializer
from desktop.platform.core.presentation.protocol.handshake import FrontendHandshake

class ConnectionManager:
    """
    Manages active websocket connections, routing messages based on ownership tokens,
    processing heartbeats, and handling ACK/NACK flows.
    """
    def __init__(self, transport: IFrontendTransport, serializer: ProtocolSerializer):
        self.transport = transport
        self.serializer = serializer
        self.active_connections: Dict[str, FrontendHandshake] = {}
        
        # Bind to transport incoming messages
        self.transport.register_event_handler(self.handle_incoming_message)

    def handle_incoming_message(self, raw_json: Dict[str, Any]):
        """
        Intercepts raw websocket messages. Processes protocol-level messages (handshake, heartbeat, ACKs)
        and forwards application-level events up to the PresentationSessionRuntime.
        """
        msg_type = raw_json.get("message_type")
        
        if msg_type == "HandshakeRequest":
            self._handle_handshake(raw_json)
        elif msg_type == "Heartbeat":
            self._handle_heartbeat(raw_json)
        elif msg_type.startswith("ACK_"):
            self._handle_ack(raw_json)
        else:
            # It's an application event (e.g. ClickEvent), deserialize and push to SessionRuntime
            try:
                event = self.serializer.deserialize_event(raw_json)
                logging.info(f"Received application event: {event}")
                # Real implementation would emit this via EventBus to PresentationSessionRuntime
            except Exception as e:
                logging.error(f"Failed to deserialize event: {e}")

    def _handle_handshake(self, raw_json: Dict[str, Any]):
        # Extract RendererCapabilities and register connection
        payload = raw_json.get("payload", {})
        instance_id = payload.get("renderer_instance_id")
        logging.info(f"Frontend connection established: {instance_id}")
        # Send HandshakeResponse ACK

    def _handle_heartbeat(self, raw_json: Dict[str, Any]):
        # Update connection last_seen timestamp
        pass

    def _handle_ack(self, raw_json: Dict[str, Any]):
        # Route ACK (e.g., ACK_VISIBLE) to SessionBarrier to unblock Behavior Runtime
        msg_type = raw_json.get("message_type")
        correlation_id = raw_json.get("correlation_id")
        logging.debug(f"Received {msg_type} for command {correlation_id}")
