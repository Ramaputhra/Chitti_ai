import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

class AlertSeverity:
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass(frozen=True)
class TelemetryEvent:
    severity: str
    category: str
    source_service: str
    payload: Dict[str, Any]
    interaction_id: Optional[str] = None
    pipeline_correlation_id: Optional[str] = None
    event_id: str = field(default_factory=lambda: "evt_" + str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class StructuredLogger:
    def __init__(self):
        self._logs = []

    def emit(self, event: TelemetryEvent):
        # Memory-buffered rotation policy logic (simulating file rotation logic)
        self._logs.append(event)
        if len(self._logs) > 100:
            self._logs.pop(0)

    def get_recent(self):
        return self._logs
