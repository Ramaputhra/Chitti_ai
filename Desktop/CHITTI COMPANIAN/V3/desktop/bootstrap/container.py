from dataclasses import dataclass
from typing import List, Any, Dict
from desktop.bootstrap.lifecycle import HealthState

@dataclass
class ServiceDeclaration:
    identifier: str
    dependencies: List[str]
    initialization_order: int
    shutdown_order: int
    instance: Any = None

class ServiceRegistry:
    def __init__(self):
        self._services: Dict[str, ServiceDeclaration] = {}
        self.health_state = HealthState.HEALTHY

    def register(self, decl: ServiceDeclaration):
        self._services[decl.identifier] = decl

    def get_all(self):
        return list(self._services.values())

    def get(self, identifier: str):
        return self._services.get(identifier).instance if identifier in self._services else None

class DependencyContainer:
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry

    def validate_circular_dependencies(self, declarations: List[ServiceDeclaration]):
        for decl in declarations:
            for dep in decl.dependencies:
                if dep == decl.identifier:
                    raise ValueError(f"Circular dependency in {decl.identifier}")

    def wire(self, declarations: List[ServiceDeclaration]):
        self.validate_circular_dependencies(declarations)
        sorted_decls = sorted(declarations, key=lambda x: x.initialization_order)
        
        for decl in sorted_decls:
            if not decl.instance:
                if decl.identifier == "ObservabilityManager":
                    from desktop.observability.manager import ObservabilityManager
                    obs_manager = ObservabilityManager(self.registry)
                    obs_manager.start()
                    decl.instance = obs_manager
                else:
                    decl.instance = f"MockInstance_{decl.identifier}"
            self.registry.register(decl)
