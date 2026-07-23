import time
import logging
from desktop.models.presentation import PresentationSession, PresentationSynchronizationMode

class SessionBarrier:
    """
    Rule 315: Presentation Synchronization Ownership.
    Ensures Narration does not begin until the UI is actually ready, or the timeout expires.
    """
    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    def _emit(self, event_name: str, payload: dict):
        if self.event_bus:
            self.event_bus.publish(event_name, payload)

    def evaluate_readiness(self, session: PresentationSession):
        """
        Evaluates the session's sync mode against its current state.
        Emits PresentationSynchronizationReady when constraints are met.
        In a real implementation, this would be an async background task or loop waiting on renderer signals.
        Here we stub the logic for demonstration.
        """
        mode = session.model.policy.sync_mode
        
        if mode == PresentationSynchronizationMode.NONE:
            # Immediate release
            self._release_barrier(session, reason="SYNC_MODE_NONE")
            return
            
        # Stub: Simulating waiting for renderer signals...
        # If the renderer never replies, the timeout fallback must trigger.
        # For this stub, we just immediately release it after logging the simulated wait.
        
        logging.info(f"Barrier waiting on {mode.value} for session {session.session_id}")
        # time.sleep(...) # Simulated wait
        
        self._release_barrier(session, reason=f"CONDITION_MET_{mode.value}")
        
    def handle_timeout(self, session: PresentationSession):
        """
        Invoked if the maximum wait time is exceeded before the renderer reports readiness.
        """
        logging.warning(f"Presentation barrier timeout for session {session.session_id}. Executing fallback.")
        self._release_barrier(session, reason="TIMEOUT_FALLBACK")

    def _release_barrier(self, session: PresentationSession, reason: str):
        self._emit("PresentationSynchronizationReady", {
            "session_id": session.session_id,
            "reason": reason
        })
