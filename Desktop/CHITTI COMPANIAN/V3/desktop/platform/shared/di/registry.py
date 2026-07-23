from typing import Any, Dict, NamedTuple

from desktop.platform.shared.di.exceptions import DuplicateRegistrationError
from desktop.platform.shared.di.interfaces import IServiceRegistry, ServiceLifetime


class ServiceRecord(NamedTuple):
    implementation: type | None
    instance: Any | None
    lifetime: ServiceLifetime


class ServiceRegistry(IServiceRegistry):
    def __init__(self) -> None:
        self._records: Dict[type, ServiceRecord] = {}

    def register(
        self,
        interface: type,
        implementation: type,
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
    ) -> None:
        if interface in self._records:
            raise DuplicateRegistrationError(
                f"Service {interface.__name__} is already registered."
            )
        self._records[interface] = ServiceRecord(implementation, None, lifetime)

    def register_instance(self, interface: type, instance: Any) -> None:
        if interface in self._records:
            raise DuplicateRegistrationError(
                f"Service {interface.__name__} is already registered."
            )
        self._records[interface] = ServiceRecord(None, instance, ServiceLifetime.SINGLETON)

    def get_record(self, interface: type) -> ServiceRecord | None:
        return self._records.get(interface)

    def get_all(self) -> Dict[type, ServiceRecord]:
        return dict(self._records)
