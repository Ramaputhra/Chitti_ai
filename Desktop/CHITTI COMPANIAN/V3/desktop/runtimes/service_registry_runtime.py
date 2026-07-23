from typing import List, Dict, Optional
from desktop.models.service_registry import ServiceDescriptor, ServiceQuery, ServiceLifecycle, ServiceHealth

class ServiceRegistryRuntime:
    """
    Rule 276: Every executable component must be registered.
    Rule 277: Planner selects through deterministic queries.
    Rule 278: Declarative metadata only.
    """
    def __init__(self, event_bus=None):
        self._services: Dict[str, ServiceDescriptor] = {}
        self.event_bus = event_bus

    def _emit(self, event_name: str, payload: dict):
        if self.event_bus:
            self.event_bus.publish(event_name, payload)

    def register_service(self, descriptor: ServiceDescriptor) -> bool:
        """Transitions a discovered service into REGISTERED and READY states."""
        if descriptor.id in self._services:
            self._services[descriptor.id] = descriptor
            descriptor.lifecycle = ServiceLifecycle.READY
            self._emit("ServiceUpdated", {"service_id": descriptor.id, "version": descriptor.version})
            return True

        descriptor.lifecycle = ServiceLifecycle.REGISTERED
        self._services[descriptor.id] = descriptor
        self._emit("ServiceRegistered", {"service_id": descriptor.id, "category": getattr(descriptor, 'category', 'service')})
        
        # Transition to READY if health is good
        if descriptor.health == ServiceHealth.AVAILABLE:
            descriptor.lifecycle = ServiceLifecycle.READY

        return True

    def find_services(self, query: ServiceQuery) -> List[ServiceDescriptor]:
        """
        Deterministic discovery for the Planner.
        Filters by intent, input/output types, offline requirements, etc.
        """
        results = []
        for svc in self._services.values():
            if svc.lifecycle != ServiceLifecycle.READY or svc.health != ServiceHealth.AVAILABLE:
                continue
                
            if query.offline_only and svc.requires_network:
                continue
                
            if query.requires_gpu and not svc.gpu_required:
                continue

            # In a full implementation, we'd do complex matching on intents, 
            # I/O types, and permissions here.
            
            results.append(svc)

        # Sort deterministically by cost or latency (if planner needs optimization)
        results.sort(key=lambda s: (s.cost_per_invoke, s.latency_ms))
        return results

    def update_health(self, service_id: str, health: ServiceHealth):
        if service_id in self._services:
            self._services[service_id].health = health
            self._emit("ServiceHealthChanged", {"service_id": service_id, "health": health.value})
