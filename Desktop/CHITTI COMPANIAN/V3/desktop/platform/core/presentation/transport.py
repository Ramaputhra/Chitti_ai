from abc import ABC, abstractmethod
from typing import Callable, Any, Dict
import logging

class IFrontendTransport(ABC):
    """
    Abstract interface for pushing UI updates to the frontend and receiving UI events.
    Renderer renders. Transport transports.
    """
    
    @abstractmethod
    def send_payload(self, session_id: str, payload_type: str, data: Dict[str, Any]) -> bool:
        """Send a rendering instruction or patch to the frontend."""
        pass
        
    @abstractmethod
    def register_event_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Register a callback for incoming frontend events (clicks, scrolls, etc)."""
        pass

    @abstractmethod
    def connect(self) -> bool:
        pass
        
    @abstractmethod
    def disconnect(self) -> bool:
        pass

class WebSocketTransport(IFrontendTransport):
    """
    Stub implementation for the future WebSocket bridge to Vite/Next.
    """
    def __init__(self):
        self.handlers = []
        self.connected = False
        
    def send_payload(self, session_id: str, payload_type: str, data: Dict[str, Any]) -> bool:
        if not self.connected:
            logging.warning(f"Cannot send {payload_type} to session {session_id}. Transport disconnected.")
            return False
            
        # Stub: serialize and push over active websocket connection
        logging.debug(f"[WS_TX] {session_id} | {payload_type} | {data.keys()}")
        return True

    def register_event_handler(self, handler: Callable[[Dict[str, Any]], None]):
        self.handlers.append(handler)
        
    def connect(self) -> bool:
        self.connected = True
        return True
        
    def disconnect(self) -> bool:
        self.connected = False
        return True
