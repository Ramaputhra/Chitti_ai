from enum import Enum, auto

class HealthState(Enum):
    """
    Represents the operational health and availability of a Provider.
    """
    UNKNOWN = auto()
    AVAILABLE = auto()
    LOADING = auto()
    READY = auto()
    BUSY = auto()
    DEGRADED = auto()
    FAILED = auto()
    OFFLINE = auto()


class LifecycleState(Enum):
    """
    Represents the physical lifecycle state of a Component/Model on disk and in memory.
    """
    REGISTERED = auto()
    DOWNLOADED = auto()
    VERIFIED = auto()
    LOADED = auto()
    WARM = auto()
    EXECUTING = auto()
    IDLE = auto()
    UNLOADED = auto()
