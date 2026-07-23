from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class SessionContext:
    """
    Holds the short-term memory and context for the active Conversation Session.
    As per Rule 104, this context is attached to the conversation session, and is 
    destroyed or reset when the session ends.
    """
    conversation_id: str
    current_turn_id: Optional[str] = None
    
    # Context attributes
    active_application: Optional[str] = None
    active_browser: Optional[str] = None
    active_folder: Optional[str] = None
    active_workflow: Optional[str] = None
    active_document: Optional[str] = None
    
    previous_capability: Optional[str] = None
    
    # Generic short-term memory store for capabilities to read/write
    memory: Dict[str, Any] = field(default_factory=dict)
    
    def update_from_execution(self, capability: str, metadata: Dict[str, Any]):
        """
        Updates context based on capability execution.
        """
        self.previous_capability = capability
        # E.g., if capability was application.launch, we might update active_application
        if capability == "application.launch":
            app = metadata.get("arguments", {}).get("application")
            if app:
                self.active_application = app
