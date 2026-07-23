from typing import List
from desktop.models.telemetry import InferenceTelemetryRecord

class InferenceTelemetry:
    """
    Records inference metrics (latency, tokens, confidence, outcomes)
    independently of the Planner to enable platform analytics.
    """
    def __init__(self):
        self.records: List[InferenceTelemetryRecord] = []
        
    def record(self, record: InferenceTelemetryRecord):
        self.records.append(record)
        # In a real system, this would publish to the EventBus or a TSDB
        print(f"[Telemetry] 📊 Inference completed in {record.latency_ms:.2f}ms. "
              f"Provider: {record.provider_name} | "
              f"Validation: {record.validation_outcome} | "
              f"Planner Outcome: {record.planner_outcome}")
