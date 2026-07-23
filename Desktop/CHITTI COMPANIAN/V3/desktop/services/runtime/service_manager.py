import threading
from typing import Any, Dict

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import IService, IServiceManager, ServiceState


class ServiceManager(IServiceManager):
    def __init__(self, logger: ILoggingService) -> None:
        self.logger = logger
        self._services: Dict[str, IService] = {}
        self._lock = threading.RLock()

    def register_service(self, service: IService) -> None:
        with self._lock:
            if service.name in self._services:
                self.logger.warning(f"Service {service.name} is already registered.")
                return
            self._services[service.name] = service
            self.logger.info(f"Registered service: {service.name}")

    def start_all(self) -> None:
        with self._lock:
            for name, service in self._services.items():
                if service.state != ServiceState.RUNNING:
                    try:
                        self.logger.info(f"Starting service: {name}")
                        service.initialize()
                    except Exception as e:
                        self.logger.exception(e, module="ServiceManager", service=name)

    def stop_all(self) -> None:
        with self._lock:
            # Shutdown in reverse order of registration (pseudo-dependency handling)
            for name, service in reversed(list(self._services.items())):
                if service.state != ServiceState.STOPPED:
                    try:
                        self.logger.info(f"Stopping service: {name}")
                        service.shutdown()
                    except Exception as e:
                        self.logger.exception(e, module="ServiceManager", service=name)

    def restart(self, service_name: str) -> None:
        with self._lock:
            service = self._services.get(service_name)
            if not service:
                self.logger.warning(f"Cannot restart unknown service: {service_name}")
                return
            try:
                service.shutdown()
                service.initialize()
                self.logger.info(f"Restarted service: {service_name}")
            except Exception as e:
                self.logger.exception(e, module="ServiceManager", service=service_name)

    def get_health(self) -> Dict[str, Dict[str, Any]]:
        health_report = {}
        with self._lock:
            for name, service in self._services.items():
                try:
                    health_report[name] = service.health_check()
                    health_report[name]["state"] = service.state.name
                except Exception as e:
                    health_report[name] = {"state": "ERROR", "exception": str(e)}
        return health_report
