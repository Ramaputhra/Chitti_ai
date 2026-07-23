import logging
from typing import Dict, Any, List
from desktop.models.presentation import (
    PresentationSession, SessionStatus, FrontendEvent, ClickEvent, FilterEvent, TabChangedEvent
)
from desktop.runtimes.presentation.session_barrier import SessionBarrier

class PresentationIntentMapper:
    """
    Rule 317: Distinguishes between local UI visual state changes and platform actions.
    """
    def __init__(self, event_bus):
        self.event_bus = event_bus

    def map_event(self, session: PresentationSession, event: FrontendEvent):
        """
        Processes frontend events and mutates the SessionContext locally,
        or promotes the event to a PresentationIntent.
        """
        # 1. Local UI Interaction (Rule 317)
        if isinstance(event, ClickEvent):
            session.context.selected_item = event.target_id
            logging.info(f"Local Context Update: Session {session.session_id} selected {event.target_id}")
            # Do NOT fire a platform workflow.
            
        elif isinstance(event, FilterEvent):
            session.context.filters[event.filter_key] = event.filter_value
            logging.info(f"Local Context Update: Session {session.session_id} filter updated")
            
        # 2. Platform Action Promotion
        # If the click was on an "export_button" or "save_button", promote it.
        if getattr(event, 'action_type', '') in ["EXPORT", "SAVE", "PRINT", "EXECUTE"]:
            logging.info(f"Promoting UI event {event.action_type} to IntentRuntime for {session.session_id}")
            if self.event_bus:
                self.event_bus.publish("PresentationIntentDispatched", {
                    "session_id": session.session_id,
                    "action": event.action_type,
                    "context": session.context.__dict__
                })

class PresentationSessionRuntime:
    """
    Rule 316: Owns the user's visual context independently of the renderer.
    Manages the session stack and frontend interactions.
    """
    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.barrier = SessionBarrier(event_bus)
        self.intent_mapper = PresentationIntentMapper(event_bus)
        
        # Session Stack Management
        self.sessions: Dict[str, PresentationSession] = {}
        self.active_session_id: str = None
        
    def register_session(self, session: PresentationSession):
        """Register a newly generated session into the stack."""
        self.sessions[session.session_id] = session
        self.focus_session(session.session_id)
        
    def focus_session(self, session_id: str):
        """Brings a session to the ACTIVE foreground, putting others in BACKGROUND."""
        if self.active_session_id and self.active_session_id in self.sessions:
            self.sessions[self.active_session_id].status = SessionStatus.BACKGROUND
            
        session = self.sessions.get(session_id)
        if session:
            session.status = SessionStatus.ACTIVE
            self.active_session_id = session_id
            logging.info(f"Focused session {session_id}")

    def handle_frontend_event(self, event: FrontendEvent):
        """
        Entrypoint for the Transport layer to push UI events back to the session.
        """
        session = self.sessions.get(event.session_id)
        if not session:
            logging.warning(f"Received event for unknown session: {event.session_id}")
            return
            
        self.intent_mapper.map_event(session, event)
