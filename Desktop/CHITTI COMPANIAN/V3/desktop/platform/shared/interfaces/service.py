from enum import Enum
from typing import Any, Dict, Protocol


class ServiceState(Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    FAILED = "FAILED"


class IService(Protocol):
    """
    Standard interface for all long-running subsystems in CHITTI.
    Allows the ServiceManager to generically orchestrate the application.
    """
    @property
    def name(self) -> str: ...

    @property
    def state(self) -> ServiceState: ...

    def initialize(self) -> None:
        """
        One-time initialization of the service (e.g. allocate resources).
        """
        ...

    def start(self) -> None:
        """
        Begin normal execution of the service.
        """
        ...

    def pause(self) -> None:
        """
        Temporarily halt execution without releasing core resources.
        """
        ...

    def resume(self) -> None:
        """
        Resume execution after a pause.
        """
        ...

    def recover(self) -> None:
        """
        Attempt to recover from an ERROR or transient failure state.
        """
        ...

    def shutdown(self) -> None: ...

    def health_check(self) -> Dict[str, Any]: ...


class IServiceManager(Protocol):
    """
    Orchestrates the lifecycle, dependencies, and health of all registered IService instances.
    """
    def register_service(self, service: IService) -> None: ...

    def start_all(self) -> None: ...

    def stop_all(self) -> None: ...

    def restart(self, service_name: str) -> None: ...

    def get_health(self) -> Dict[str, Dict[str, Any]]: ...
