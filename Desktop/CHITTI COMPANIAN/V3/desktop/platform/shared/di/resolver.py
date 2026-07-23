import inspect
from typing import Any, Dict, Set, TypeVar

from desktop.platform.shared.di.exceptions import CircularDependencyError, MissingDependencyError
from desktop.platform.shared.di.interfaces import IServiceResolver, ServiceLifetime
from desktop.platform.shared.di.registry import ServiceRegistry

T = TypeVar("T")


class ServiceResolver(IServiceResolver):
    def __init__(self, registry: ServiceRegistry) -> None:
        self._registry = registry
        self._singletons: Dict[type, Any] = {}
        self._resolving: Set[type] = set()

    def resolve(self, interface: type[T]) -> T:
        if interface in self._resolving:
            raise CircularDependencyError(
                f"Circular dependency detected for {interface.__name__}"
            )

        record = self._registry.get_record(interface)
        if not record:
            raise MissingDependencyError(f"No registration found for {interface.__name__}")

        if record.lifetime == ServiceLifetime.SINGLETON:
            if record.instance is not None:
                return record.instance  # type: ignore
            if interface in self._singletons:
                return self._singletons[interface]

        self._resolving.add(interface)

        try:
            if record.implementation is None:
                raise MissingDependencyError(
                    f"Implementation missing for {interface.__name__}"
                )

            # Inspect constructor to resolve dependencies recursively
            init_signature = inspect.signature(record.implementation.__init__)
            params = init_signature.parameters

            kwargs = {}
            for name, param in params.items():
                if name == "self":
                    continue
                param_type = param.annotation
                if param_type == inspect.Parameter.empty:
                    raise MissingDependencyError(
                        f"Parameter '{name}' in {record.implementation.__name__} lacks type annotation."
                    )

                kwargs[name] = self.resolve(param_type)

            instance = record.implementation(**kwargs)

            if record.lifetime == ServiceLifetime.SINGLETON:
                self._singletons[interface] = instance

            return instance  # type: ignore

        finally:
            self._resolving.remove(interface)
