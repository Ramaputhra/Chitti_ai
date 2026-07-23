from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Type

class RuntimeState(Enum):
    CREATED = 1
    INITIALIZING = 2
    READY = 3
    STARTING = 4
    RUNNING = 5
    STOPPING = 6
    STOPPED = 7
    FAILED = 8

class HealthState(Enum):
    HEALTHY = 1
    DEGRADED = 2
    FAILED = 3

class IRuntime(ABC):
    """
    Standard interface for all CHITTI runtimes (Rule 172).
    """
    
    @property
    @abstractmethod
    def dependencies(self) -> List[Type['IRuntime']]:
        """Returns explicitly required service interfaces (Rule 173)."""
        pass

    @abstractmethod
    async def initialize(self, context) -> bool:
        """Called by BootManager before readiness barrier."""
        pass

    @abstractmethod
    async def start(self) -> bool:
        """Called by BootManager after all runtimes report READY."""
        pass

    @abstractmethod
    async def stop(self) -> bool:
        """Called by Kernel during normal shutdown sequence."""
        pass

    @abstractmethod
    def health(self) -> HealthState:
        """Called periodically by Kernel."""
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """Called to completely deallocate resources."""
        pass
