import os
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
import time
from datetime import datetime
from desktop.platform.shared.interfaces.event_bus import Event

class PresencePriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class PresenceContext:
    """
    Context that can optionally accompany a PresenceState.
    e.g. state=WORKING, context=PresenceContext(task="Copy Files", progress=72, eta="3 min")
    """
    task: Optional[str] = None
    progress: Optional[int] = None
    eta: Optional[str] = None
    message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class StateMetadata:
    animation_profile: str
    priority: PresencePriority
    interruptible: bool
    min_duration_ms: int
    speech_allowed: bool

class PresenceState(Enum):
    OFFLINE = auto()
    STARTING = auto()
    READY = auto()
    IDLE = auto()
    LISTENING = auto()
    UNDERSTANDING = auto()
    THINKING = auto()
    WORKING = auto()
    READING = auto()
    WRITING = auto()
    MONITORING = auto()
    TALKING = auto()
    SUCCESS = auto()
    FAILURE = auto()
    WAITING = auto()
    EXERCISING = auto()
    SLEEPING = auto()
    GOODBYE = auto()
    ERROR = auto()

    @property
    def metadata(self) -> StateMetadata:
        return _STATE_METADATA_MAP[self]

_STATE_METADATA_MAP = {
    PresenceState.OFFLINE: StateMetadata("fade_out", PresencePriority.CRITICAL, False, 0, False),
    PresenceState.STARTING: StateMetadata("spin", PresencePriority.CRITICAL, False, 1000, False),
    
    PresenceState.ERROR: StateMetadata("shake_red", PresencePriority.CRITICAL, True, 2000, True),
    
    PresenceState.LISTENING: StateMetadata("expand_blue", PresencePriority.HIGH, True, 500, False),
    PresenceState.TALKING: StateMetadata("waveform", PresencePriority.HIGH, True, 100, True),
    PresenceState.FAILURE: StateMetadata("flash_orange", PresencePriority.HIGH, True, 1500, True),
    
    PresenceState.UNDERSTANDING: StateMetadata("swirl_blue", PresencePriority.MEDIUM, True, 300, False),
    PresenceState.THINKING: StateMetadata("pulse_purple", PresencePriority.MEDIUM, True, 600, False),
    PresenceState.WORKING: StateMetadata("progress_ring", PresencePriority.MEDIUM, True, 500, False),
    PresenceState.READING: StateMetadata("scan_line", PresencePriority.MEDIUM, True, 500, False),
    PresenceState.WRITING: StateMetadata("typewriter", PresencePriority.MEDIUM, True, 500, False),
    PresenceState.SUCCESS: StateMetadata("pop_green", PresencePriority.MEDIUM, False, 1200, True),
    PresenceState.MONITORING: StateMetadata("slow_breathe", PresencePriority.MEDIUM, True, 1000, False),
    
    PresenceState.READY: StateMetadata("solid_glow", PresencePriority.LOW, True, 500, False),
    PresenceState.IDLE: StateMetadata("dim_glow", PresencePriority.LOW, True, 0, False),
    PresenceState.WAITING: StateMetadata("dots", PresencePriority.LOW, True, 500, False),
    PresenceState.EXERCISING: StateMetadata("bounce", PresencePriority.LOW, True, 0, False),
    PresenceState.SLEEPING: StateMetadata("slow_pulse", PresencePriority.LOW, True, 0, False),
    PresenceState.GOODBYE: StateMetadata("shrink_away", PresencePriority.CRITICAL, False, 1500, True),
}

class PresenceStateChanged(Event):
    """Event emitted by PresenceEngine when a state transition occurs."""
    def __init__(self, previous: PresenceState, current: PresenceState, reason: Optional[str] = None, metadata: Optional[dict] = None):
        super().__init__(
            event_id="Presence.StateChanged",
            source="PresenceEngine",
            payload={
                "previous": previous.name if previous else None,
                "current": current.name,
                "reason": reason,
                "metadata": metadata or {}
            }
        )
        self.previous = previous
        self.current = current
        self.reason = reason
        self.metadata = metadata or {}
        # Also store a python datetime for easy subscriber use
        self.datetime_timestamp = datetime.now()
