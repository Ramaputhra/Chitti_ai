from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class SpeechMetrics:
    """
    S36A: Telemetry metrics for Voice Runtime (Latency, Queue Depth, Synthesis Time, Failure Count, Retry Count, Cache Hits).
    """
    latency_ms: float = 0.0
    queue_depth: int = 0
    synthesis_time_ms: float = 0.0
    failure_count: int = 0
    retry_count: int = 0
    cache_hit_count: int = 0
    cache_miss_count: int = 0

    def record_synthesis(self, synthesis_ms: float, latency_ms: float):
        self.synthesis_time_ms = synthesis_ms
        self.latency_ms = latency_ms

    def record_failure(self):
        self.failure_count += 1

    def record_cache_hit(self):
        self.cache_hit_count += 1

    def record_cache_miss(self):
        self.cache_miss_count += 1
