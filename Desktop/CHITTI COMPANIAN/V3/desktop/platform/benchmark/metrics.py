from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ProviderBenchmark:
    """
    Lightweight telemetry representing the engineering performance 
    of a specific Provider/Model execution.
    """
    model_id: str
    provider_backend: str
    
    # Timing
    model_load_time_ms: float = 0.0
    first_inference_latency_ms: float = 0.0
    average_inference_latency_ms: float = 0.0
    
    # Resource Peaks
    peak_ram_mb: float = 0.0
    peak_cpu_percent: float = 0.0
    model_size_mb: float = 0.0
    
    # Stats
    throughput_req_sec: float = 0.0
    error_rate_percent: float = 0.0
    
    # Distributions
    confidence_distribution: List[float] = field(default_factory=list)
    
    def add_confidence(self, score: float):
        self.confidence_distribution.append(score)
        
    def add_latency(self, latency_ms: float, is_first: bool = False):
        if is_first:
            self.first_inference_latency_ms = latency_ms
        else:
            # Simple moving average for lightweight tracking
            if self.average_inference_latency_ms == 0.0:
                self.average_inference_latency_ms = latency_ms
            else:
                self.average_inference_latency_ms = (self.average_inference_latency_ms * 0.9) + (latency_ms * 0.1)
