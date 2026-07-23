import logging
from typing import Callable, Any, Dict
from desktop.platform.core.presentation.transport.base import IFrontendTransport

class WebSocketTransport(IFrontendTransport):
    """
    WebSocket transport implementation for the Vite/Next frontend.
    Operates strictly on the FrontendProtocolMessage format (Rule 321).
    """
    def __init__(self):
        self.handlers = []
        self.connected = False
        
    def send_message(self, serialized_message: Dict[str, Any]) -> bool:
        if not self.connected:
            logging.warning(f"Cannot send message {serialized_message.get('message_id')}. Transport disconnected.")
            return False
            
        # Stub: serialize dict to string and push over active websocket connection
        msg_type = serialized_message.get('message_type')
        sess_id = serialized_message.get('session_id')
        logging.debug(f"[WS_TX] {sess_id} | {msg_type}")
        return True

    def register_event_handler(self, handler: Callable[[Dict[str, Any]], None]):
        self.handlers.append(handler)
        
    def connect(self) -> bool:
        self.connected = True
        return True
        
    def disconnect(self) -> bool:
        self.connected = False
        return True
