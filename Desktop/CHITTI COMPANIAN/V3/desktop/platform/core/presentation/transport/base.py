from abc import ABC, abstractmethod
from typing import Callable, Any, Dict

class IFrontendTransport(ABC):
    """
    Abstract interface for pushing UI updates to the frontend and receiving UI events.
    Renderer renders. Transport transports.
    Now operates on serialized FrontendProtocolMessages.
    """
    
    @abstractmethod
    def send_message(self, serialized_message: Dict[str, Any]) -> bool:
        """Send a serialized FrontendProtocolMessage to the frontend."""
        pass
        
    @abstractmethod
    def register_event_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Register a callback for incoming raw websocket JSON."""
        pass

    @abstractmethod
    def connect(self) -> bool:
        pass
        
    @abstractmethod
    def disconnect(self) -> bool:
        pass
