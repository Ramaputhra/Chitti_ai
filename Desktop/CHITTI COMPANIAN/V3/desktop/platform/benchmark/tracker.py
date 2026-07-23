import time
import functools
import logging
from typing import Dict, Any, Callable
from desktop.platform.benchmark.metrics import ProviderBenchmark
from desktop.models.ai_result import AIResult

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)

class BenchmarkTracker:
    """
    A lightweight utility to track provider performance.
    It does not store heavy historical data, but rather tracks active/recent performance
    so we can evaluate capability health.
    """
    def __init__(self):
        # Maps component_id -> ProviderBenchmark
        self._benchmarks: Dict[str, ProviderBenchmark] = {}

    def get_benchmark(self, component_id: str, backend: str) -> ProviderBenchmark:
        if component_id not in self._benchmarks:
            self._benchmarks[component_id] = ProviderBenchmark(
                model_id=component_id,
                provider_backend=backend
            )
        return self._benchmarks[component_id]

    def record_load_time(self, component_id: str, backend: str, load_time_ms: float):
        bm = self.get_benchmark(component_id, backend)
        bm.model_load_time_ms = load_time_ms
        logger.info(f"[{component_id}] Loaded in {load_time_ms:.2f}ms")

    def track_inference(self, component_id: str, backend: str):
        """
        Context manager / decorator logic to wrap an inference call.
        Tracks execution latency, CPU, and RAM peaks.
        """
        bm = self.get_benchmark(component_id, backend)
        
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> AIResult:
                start_time = time.perf_counter()
                
                # Baseline resources
                if HAS_PSUTIL:
                    process = psutil.Process()
                    baseline_ram = process.memory_info().rss / (1024 * 1024)
                    psutil.cpu_percent(interval=None) # Reset CPU counter
                
                is_first = (bm.first_inference_latency_ms == 0.0)
                
                try:
                    result: AIResult = func(*args, **kwargs)
                    latency_ms = (time.perf_counter() - start_time) * 1000
                    
                    bm.add_latency(latency_ms, is_first=is_first)
                    if hasattr(result, "confidence"):
                        bm.add_confidence(result.confidence)
                        
                    # Peak resources
                    if HAS_PSUTIL:
                        peak_ram = process.memory_info().rss / (1024 * 1024)
                        cpu_percent = psutil.cpu_percent(interval=None)
                        bm.peak_ram_mb = max(bm.peak_ram_mb, peak_ram)
                        bm.peak_cpu_percent = max(bm.peak_cpu_percent, cpu_percent)
                        
                    return result
                except Exception as e:
                    # Very naive error rate tracking
                    bm.error_rate_percent = min(100.0, bm.error_rate_percent + 1.0)
                    raise e
                    
            return wrapper
        return decorator
