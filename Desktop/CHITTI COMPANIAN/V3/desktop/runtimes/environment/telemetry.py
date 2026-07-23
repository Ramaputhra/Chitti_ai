class EnvironmentTelemetry:
    """
    Captures latency, success rates, resource locking overhead, and crash counts
    for the environment adapters.
    """
    def record_action(self, action_id: str, success: bool, latency_ms: float):
        pass
