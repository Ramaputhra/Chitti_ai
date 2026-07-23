from dataclasses import dataclass

class MetricType:
    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    HISTOGRAM = "HISTOGRAM"

@dataclass(frozen=True)
class MetricDefinition:
    identifier: str
    metric_type: str
    units: str
    aggregation_policy: str
    retention_policy: str

class MetricsRegistry:
    def __init__(self):
        self._definitions = {}
        self._values = {}

    def register(self, definition: MetricDefinition):
        self._definitions[definition.identifier] = definition
        self._values[definition.identifier] = [] if definition.metric_type == MetricType.HISTOGRAM else 0

    def record(self, identifier: str, value: float):
        if identifier not in self._definitions:
            return
        
        defn = self._definitions[identifier]
        if defn.metric_type == MetricType.COUNTER:
            self._values[identifier] += value
        elif defn.metric_type == MetricType.GAUGE:
            self._values[identifier] = value
        elif defn.metric_type == MetricType.HISTOGRAM:
            self._values[identifier].append(value)
            if len(self._values[identifier]) > 1000:
                self._values[identifier].pop(0)

    def get_snapshot(self):
        return {k: v for k, v in self._values.items()}
