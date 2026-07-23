import logging
from enum import Enum
from dataclasses import dataclass
from desktop.platform.shared.interfaces.event_bus import IEventBus, Event
from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.models.biometrics import SpeakerState

logger = logging.getLogger(__name__)

class PolicyDecisionState(Enum):
    ALLOWED = "ALLOWED"
    READ_ONLY = "READ_ONLY"
    CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"
    DENIED = "DENIED"

@dataclass
class PolicyDecision:
    action_domain: str
    state: PolicyDecisionState
    reason: str

class PolicyRuntime:
    """
    Centralized security, authentication, and permission evaluation for protected desktop actions.
    (See Rule 14: Authentication decisions belong exclusively to the Policy Runtime).
    """
    def __init__(self, event_bus: IEventBus):
        self.event_bus = event_bus
        self._current_speaker_state = SpeakerState.UNKNOWN
        
        if hasattr(self.event_bus, "subscribe"):
            self.event_bus.subscribe(SystemEvents.VOICE_SPEAKER_VERIFIED, self._on_speaker_verified)
            
    def start(self):
        logger.info("PolicyRuntime started.")
        
    def stop(self):
        logger.info("PolicyRuntime stopped.")

    def _on_speaker_verified(self, event: Event):
        state_str = event.payload.get("state", "UNKNOWN")
        try:
            self._current_speaker_state = SpeakerState(state_str)
            logger.info(f"[PolicyRuntime] Updated active speaker state: {self._current_speaker_state.value}")
        except ValueError:
            self._current_speaker_state = SpeakerState.UNKNOWN

    def evaluate_action(self, action_domain: str, requires_auth: bool = False) -> PolicyDecision:
        """
        Evaluate if the current active user is allowed to perform the action.
        """
        # If action doesn't require explicit auth, allow it
        if not requires_auth:
            return PolicyDecision(action_domain, PolicyDecisionState.ALLOWED, "No auth required")
            
        # If action requires auth, evaluate speaker state
        if self._current_speaker_state == SpeakerState.VERIFIED:
            return PolicyDecision(action_domain, PolicyDecisionState.ALLOWED, "Authenticated via voice")
            
        if self._current_speaker_state == SpeakerState.UNKNOWN:
            # Maybe allow read-only or prompt for confirmation
            return PolicyDecision(action_domain, PolicyDecisionState.CONFIRMATION_REQUIRED, "Speaker unknown")
            
        return PolicyDecision(action_domain, PolicyDecisionState.DENIED, "Speaker rejected")
