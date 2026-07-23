from typing import Dict, Type, Any, Callable
from desktop.core.providers import IConfigProvider, INormalizationProvider, IIntentRegistry
from desktop.core.eventbus import IEventBus, EventBus
from desktop.core.config.manager import ConfigManager
from pathlib import Path

class DIContainer:
    """
    Enforces Rule 243 - Constructor Injection Only.
    """
    def __init__(self, config_dir: Path):
        self._services: Dict[Type, Any] = {}
        self.config_dir = config_dir
        
    def register_singleton(self, interface_type: Type, instance: Any):
        self._services[interface_type] = instance
        
    def resolve(self, interface_type: Type) -> Any:
        if interface_type not in self._services:
            raise Exception(f"Service {interface_type} not registered in DI Container.")
        return self._services[interface_type]

    def build_core_infrastructure(self):
        # Build core dependencies topologically
        event_bus = EventBus()
        self.register_singleton(IEventBus, event_bus)
        
        config_manager = ConfigManager(self.config_dir)
        # We would wrap ConfigManager into an IConfigProvider here
        # self.register_singleton(IConfigProvider, config_manager_wrapper)
        
        return self
