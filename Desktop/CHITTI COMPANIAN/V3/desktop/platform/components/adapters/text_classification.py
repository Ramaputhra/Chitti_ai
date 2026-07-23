from typing import Any
import logging
from desktop.platform.components.adapter import ProviderAdapter
from desktop.models.ai_context import RuntimeContext
from desktop.models.ai_result import AIResult, InferenceMetadata
from desktop.models.ai_payloads import IntentClassification
from desktop.models.component_states import HealthState
from desktop.platform.benchmark.tracker import BenchmarkTracker

logger = logging.getLogger(__name__)

class TextClassificationProvider(ProviderAdapter):
    """
    Model-agnostic adapter for Text Classification (e.g. ModernBERT, TinyBERT).
    Uses Hugging Face Transformers pipeline under the hood, but abstracts it
    completely from the rest of CHITTI.
    """
    def __init__(self, model_name_or_path: str, component_id: str, tracker: BenchmarkTracker):
        self.model_path = model_name_or_path
        self.component_id = component_id
        self.tracker = tracker
        self._health = HealthState.UNKNOWN
        self.pipeline = None

    def initialize(self) -> None:
        self._health = HealthState.LOADING
        import time
        start = time.perf_counter()
        
        try:
            # We import here to delay loading heavy ML libraries until strictly needed
            from transformers import pipeline
            # Use a fast distilbert if ModernBERT isn't locally cached yet for the demo,
            # or rely on the specified path. 
            # (In production, model_name_or_path comes from the manifest)
            self.pipeline = pipeline("text-classification", model=self.model_path)
            
            load_time = (time.perf_counter() - start) * 1000
            self.tracker.record_load_time(self.component_id, "transformers", load_time)
            
            self._health = HealthState.AVAILABLE
            logger.info(f"{self.component_id} initialized successfully in {load_time:.2f}ms")
        except Exception as e:
            logger.error(f"Failed to load {self.component_id}: {e}")
            self._health = HealthState.FAILED

    def health_check(self) -> HealthState:
        return self._health

    def warm(self) -> None:
        if self._health != HealthState.AVAILABLE:
            return
            
        try:
            # Dummy inference to compile kernels / allocate VRAM
            self.pipeline("warmup sequence")
            self._health = HealthState.READY
        except Exception as e:
            logger.error(f"Failed to warm up {self.component_id}: {e}")
            self._health = HealthState.FAILED

    def execute(self, payload: str, context: RuntimeContext) -> AIResult[IntentClassification]:
        if self._health != HealthState.READY:
            raise RuntimeError(f"Provider {self.component_id} is not ready (State: {self._health})")
            
        self._health = HealthState.BUSY
        
        # Wrapped by tracker externally, but we do the inference here
        try:
            # Result format: [{'label': 'OPEN_FOLDER', 'score': 0.99}]
            raw_result = self.pipeline(payload)[0]
            
            intent = raw_result['label']
            confidence = raw_result['score']
            
            metadata = InferenceMetadata(
                model_id=self.component_id,
                provider_backend="transformers",
                latency_ms=0.0, # Filled by tracker
                cached=False
            )
            
            payload_obj = IntentClassification(
                intent=intent,
                confidence=confidence,
                entities={} # Entity extraction is a separate capability or extracted via rules
            )
            
            self._health = HealthState.READY
            return AIResult(payload=payload_obj, confidence=confidence, metadata=metadata)
            
        except Exception as e:
            self._health = HealthState.DEGRADED
            logger.error(f"Execution failed in {self.component_id}: {e}")
            raise e

    def unload(self) -> None:
        self.pipeline = None
        self._health = HealthState.OFFLINE
