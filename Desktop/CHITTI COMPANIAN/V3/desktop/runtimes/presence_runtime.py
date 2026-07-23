import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Set

from desktop.models.lifecycle import IRuntime, HealthState
from desktop.app.context import KernelContext
from desktop.models.events import SystemEvent
from desktop.models.presence import (
    RawPresenceSignal,
    DerivedPresenceState,
    PresenceStateSnapshot,
    PresenceSession
)

logger = logging.getLogger(__name__)

class PresenceEvent(SystemEvent):
    def __init__(self, state_snapshot: PresenceStateSnapshot):
        super().__init__()
        self.event_type = "PresenceStateChanged"
        self.data = {
            "raw_signal": state_snapshot.raw_signal.value,
            "derived_states": [s.value for s in state_snapshot.derived_states],
            "timestamp": state_snapshot.timestamp
        }

class PresenceRuntime(IRuntime):
    """
    Sprint 7.2: Presence Runtime.
    Tracks raw desktop signals and derives contextual states (Morning, Weekend, Away, etc).
    Emits PresenceStateChanged events for the ExperienceRuntime to consume.
    """
    def __init__(self):
        self.context: Optional[KernelContext] = None
        self._running = False
        self._current_snapshot = PresenceStateSnapshot()
        self._sessions: List[PresenceSession] = []
        self._current_session: Optional[PresenceSession] = None

    @property
    def dependencies(self) -> List[Any]:
        return []

    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        return True

    async def start(self) -> bool:
        self._running = True
        logger.info("PresenceRuntime started.")
        # Simulate initial startup evaluation
        await self.process_raw_signal(RawPresenceSignal.STARTUP)
        return True

    async def stop(self) -> bool:
        self._running = False
        await self.process_raw_signal(RawPresenceSignal.SHUTDOWN)
        return True

    def health(self) -> HealthState:
        return HealthState.HEALTHY

    async def shutdown(self) -> bool:
        return True

    async def process_raw_signal(self, signal: RawPresenceSignal):
        """
        Receives raw signals from desktop integrations (e.g., locking screen, sleep mode).
        """
        if not self._running:
            return
            
        logger.debug(f"Received raw presence signal: {signal.value}")
        
        # Derive time-based states
        derived = self._derive_time_states()
        
        # Derive availability states based on signal
        if signal in (RawPresenceSignal.IDLE, RawPresenceSignal.LOCKED, RawPresenceSignal.SLEEP, RawPresenceSignal.LOGOUT):
            derived.add(DerivedPresenceState.AWAY)
        else:
            derived.add(DerivedPresenceState.AVAILABLE)
            
        self._current_snapshot = PresenceStateSnapshot(
            timestamp=time.time(),
            raw_signal=signal,
            derived_states=derived
        )
        
        # Manage sessions
        if self._current_session:
            self._current_session.end_time = time.time()
            self._sessions.append(self._current_session)
            
        self._current_session = PresenceSession(signal=signal)
        
        logger.info(f"Presence state updated: {signal.value} -> {[s.value for s in derived]}")
        
        if self.context and hasattr(self.context, 'event_bus') and self.context.event_bus:
            event = PresenceEvent(self._current_snapshot)
            # await self.context.event_bus.publish(event.event_type, event)
            pass

    def time_since_last_state(self, target_state: DerivedPresenceState) -> float:
        """Returns seconds since the target derived state was last active. Returns -1 if never seen."""
        if target_state in self._current_snapshot.derived_states:
            return 0.0
            
        # We would need to reconstruct derived states for past sessions for full accuracy,
        # but for now we approximate based on raw signals that imply AWAY/AVAILABLE.
        # This is a stub for the logic.
        return -1.0

    def _derive_time_states(self) -> Set[DerivedPresenceState]:
        states = set()
        now = datetime.now()
        
        # Time of day
        hour = now.hour
        if 5 <= hour < 12:
            states.add(DerivedPresenceState.MORNING)
        elif 12 <= hour < 17:
            states.add(DerivedPresenceState.AFTERNOON)
        elif 17 <= hour < 21:
            states.add(DerivedPresenceState.EVENING)
        else:
            states.add(DerivedPresenceState.NIGHT)
            
        # Day of week
        if now.weekday() >= 5: # 5=Sat, 6=Sun
            states.add(DerivedPresenceState.WEEKEND)
        else:
            if 9 <= hour < 17:
                states.add(DerivedPresenceState.WORKING_HOURS)
                
        # Note: HOLIDAY requires calendar integration (Future)
        
        return states

    def get_current_state(self) -> PresenceStateSnapshot:
        return self._current_snapshot
