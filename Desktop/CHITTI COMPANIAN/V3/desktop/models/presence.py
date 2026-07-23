from enum import Enum
from dataclasses import dataclass, field
import time

class RawPresenceSignal(Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    UNLOCKED = "UNLOCKED"
    SLEEP = "SLEEP"
    RESUME = "RESUME"
    SHUTDOWN = "SHUTDOWN"
    STARTUP = "STARTUP"
    TIMEZONE_CHANGED = "TIMEZONE_CHANGED"

class DerivedPresenceState(Enum):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"
    NIGHT = "NIGHT"
    WORKING_HOURS = "WORKING_HOURS"
    WEEKEND = "WEEKEND"
    HOLIDAY = "HOLIDAY"
    AWAY = "AWAY"
    AVAILABLE = "AVAILABLE"

@dataclass
class PresenceStateSnapshot:
    """
    Represents the current combined state of the user's presence.
    """
    timestamp: float = field(default_factory=time.time)
    raw_signal: RawPresenceSignal = RawPresenceSignal.STARTUP
    derived_states: set[DerivedPresenceState] = field(default_factory=set)
    timezone: str = "UTC"

@dataclass
class PresenceSession:
    """
    Represents a duration of time spent in a specific raw state.
    """
    signal: RawPresenceSignal
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    
    @property
    def duration(self) -> float:
        if self.end_time == 0.0:
            return time.time() - self.start_time
        return self.end_time - self.start_time
