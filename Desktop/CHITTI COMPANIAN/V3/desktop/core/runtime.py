from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Optional, Dict, Any, List

class RuntimeState(Enum):
    CREATED = auto()
    INITIALIZING = auto()
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPING = auto()
    STOPPED = auto()
    FAILED = auto()
    RESTARTING = auto()

class RuntimePriority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

class RestartPolicy(Enum):
    NEVER = auto()
    ALWAYS = auto()
    ON_FAILURE = auto()
    MANUAL = auto()

@dataclass
class RuntimeTraits:
    """Explicitly declares the runtime's traits and support flags."""
    pause: bool = False
    hot_reload: bool = False
    background: bool = False
    multi_instance: bool = False

@dataclass
class HealthPolicy:
    """Configures the supervisor's active monitoring rules."""
    interval_seconds: float = 5.0
    timeout_seconds: float = 30.0
    max_retries: int = 3

@dataclass
class RuntimeMetadata:
    runtime_id: str
    api_version: str
    priority: RuntimePriority
    dependencies: List[str]
    traits: RuntimeTraits
    health_policy: HealthPolicy
    restart_policy: RestartPolicy

@dataclass
class HealthPayload:
    healthy: bool
    state: RuntimeState
    last_heartbeat: datetime
    uptime: float  # seconds
    details: Optional[Dict[str, Any]] = field(default_factory=dict)

class IRuntime(ABC):
    @abstractmethod
    def get_metadata(self) -> RuntimeMetadata:
        pass

    @abstractmethod
    def get_state(self) -> RuntimeState:
        pass

    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @abstractmethod
    async def health_check(self) -> HealthPayload:
        pass

class IPausableRuntime(IRuntime):
    @abstractmethod
    async def pause(self) -> None:
        pass

    @abstractmethod
    async def resume(self) -> None:
        pass
