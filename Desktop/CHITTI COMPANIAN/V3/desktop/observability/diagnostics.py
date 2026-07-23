import sys
import traceback
from datetime import datetime, timezone
from desktop.observability.logger import StructuredLogger
from desktop.observability.metrics import MetricsRegistry
from desktop.bootstrap.container import ServiceRegistry

class DiagnosticSnapshotGenerator:
    def __init__(self, logger: StructuredLogger, metrics: MetricsRegistry, service_registry: ServiceRegistry):
        self.logger = logger
        self.metrics = metrics
        self.service_registry = service_registry

    def generate_snapshot(self):
        recent_logs = [{"event_id": e.event_id, "severity": e.severity, "msg": str(e.payload)} for e in self.logger.get_recent()]
        services_health = self.service_registry.health_state
        
        return {
            "snapshot_version": "V2",
            "schema_version": "1.0",
            "generation_timestamp": datetime.now(timezone.utc).isoformat(),
            "active_threads": [],
            "memory_footprint_mb": 42.0,
            "service_registry_health": services_health,
            "metrics": self.metrics.get_snapshot(),
            "recent_logs": recent_logs
        }
