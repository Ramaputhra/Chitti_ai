from typing import Any, Dict, TypeVar

from desktop.platform.shared.di.interfaces import ServiceLifetime
from desktop.platform.shared.di.registry import ServiceRegistry
from desktop.platform.shared.di.resolver import ServiceResolver

T = TypeVar("T")


class DIContainer:
    """
    Composition Root Container.
    Services must be explicitly registered and resolved here.
    Business modules should NOT access this container directly.
    """

    def __init__(self) -> None:
        self.registry = ServiceRegistry()
        self.resolver = ServiceResolver(self.registry)

    def register_singleton(self, interface: type, implementation: type) -> None:
        self.registry.register(interface, implementation, ServiceLifetime.SINGLETON)

    def register_transient(self, interface: type, implementation: type) -> None:
        self.registry.register(interface, implementation, ServiceLifetime.TRANSIENT)

    def register_instance(self, interface: type, instance: Any) -> None:
        self.registry.register_instance(interface, instance)

    def resolve(self, interface: type[T]) -> T:
        return self.resolver.resolve(interface)

    def diagnostics(self) -> Dict[str, Any]:
        """Expose current state for debugging."""
        records = self.registry.get_all()
        return {
            "registered_count": len(records),
            "services": [intf.__name__ for intf in records.keys()],
        }
