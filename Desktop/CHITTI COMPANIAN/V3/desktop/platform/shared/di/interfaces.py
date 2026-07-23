from enum import Enum
from typing import Any, Protocol, TypeVar

T = TypeVar("T")


class ServiceLifetime(Enum):
    SINGLETON = "SINGLETON"
    TRANSIENT = "TRANSIENT"


class IServiceRegistry(Protocol):
    def register(
        self,
        interface: type,
        implementation: type,
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
    ) -> None: ...

    def register_instance(self, interface: type, instance: Any) -> None: ...


class IServiceResolver(Protocol):
    def resolve(self, interface: type[T]) -> T: ...
