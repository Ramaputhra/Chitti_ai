import queue
import threading
import json
from typing import Optional
from desktop.observability.logger import StructuredLogger, TelemetryEvent, AlertSeverity
from desktop.observability.metrics import MetricsRegistry
from desktop.observability.tracer import ExecutionTracer
from desktop.observability.diagnostics import DiagnosticSnapshotGenerator
from desktop.bootstrap.container import ServiceRegistry

class ObservabilityManager:
    def __init__(self, service_registry: ServiceRegistry):
        self.logger = StructuredLogger()
        self.metrics = MetricsRegistry()
        self.tracer = ExecutionTracer()
        self.diagnostics = DiagnosticSnapshotGenerator(self.logger, self.metrics, service_registry)
        self.event_queue = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="TelemetryWorkerThread")
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            # Send a poison pill
            self.event_queue.put(None)
            self._thread.join(timeout=2.0)

    def log(self, event: TelemetryEvent):
        self.event_queue.put(event)

    def handle_crash(self):
        snapshot = self.diagnostics.generate_snapshot()
        with open("diagnostic_snapshot.json", "w") as f:
            json.dump(snapshot, f, indent=2)

    def _worker_loop(self):
        while self._running:
            try:
                event = self.event_queue.get(timeout=0.1)
                if event is None:
                    continue
                self.logger.emit(event)
                
                if event.severity == AlertSeverity.CRITICAL:
                    self.handle_crash()
            except queue.Empty:
                pass
