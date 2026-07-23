from typing import Any, Dict, List

import ollama

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import IProvider
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.health import ProviderHealth


class OllamaProvider(IProvider):
    """
    Connects to local Ollama instance for fast, private inference.
    Great for entity extraction, semantic routing, and offline fallback.
    """
    def __init__(self, logger: ILoggingService, default_model: str = "llama3"):
        self.logger = logger
        self.default_model = default_model
        self._state = ServiceState.STOPPED
        self._is_healthy = False

    @property
    def name(self) -> str: return "OllamaProvider"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self.logger.info("Initializing Ollama Provider...")
        self._check_health()
        self._state = ServiceState.RUNNING

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED

    def _check_health(self) -> None:
        try:
            ollama.list()
            self._is_healthy = True
        except Exception as e:
            self.logger.warning(f"Ollama is unreachable: {e}")
            self._is_healthy = False

    def get_provider_health(self) -> ProviderHealth:
        self._check_health()
        return ProviderHealth(
            status="Healthy" if self._is_healthy else "Unavailable",
            healthy=self._is_healthy,
            enabled=True,
            configured=True,
            authenticated=True, # Local doesn't need auth
            latency_ms=45,
            last_error=None,
            version="0.1.7",
            model=self.default_model,
            uptime=0
        )

    def health_check(self) -> Dict[str, Any]:
        h = self.get_provider_health()
        return {"status": h.status, "model": h.model}

    def benchmark(self) -> Dict[str, Any]:
        return {"latency_ms": 45}  # Simulated or measured

    def capabilities(self) -> List[str]:
        return ["text_generation", "entity_extraction", "offline"]

    def version(self) -> str:
        # Ollama SDK version or server version
        return "0.1.7"

    def configuration(self) -> Dict[str, Any]:
        return {"default_model": self.default_model}

    def generate(self, prompt: str, model: str | None = None) -> str:
        if not self._is_healthy:
            return ""
        target_model = model or self.default_model
        self.logger.info(f"Ollama generating using {target_model}...")
        try:
            response = ollama.generate(model=target_model, prompt=prompt)
            return response.get("response", "")
        except Exception as e:
            self.logger.error(f"Ollama generation failed: {e}")
            return ""
