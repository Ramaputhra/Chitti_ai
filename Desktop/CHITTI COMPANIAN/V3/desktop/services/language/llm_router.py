from typing import Any, Dict, Generator, List

from desktop.platform.shared.interfaces.llm import ILLMProvider
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import ProviderStatus
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.ai import LLMRequest, LLMResponse, ResponseChunk
from desktop.platform.integrations.core.provider_registry import LLMProviderRegistry


class LLMRouter(ILLMProvider):
    def __init__(self, registry: LLMProviderRegistry, logger: ILoggingService) -> None:
        self.registry = registry
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "LLMRouter"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {"registry_status": self.registry.health_check()}

    def benchmark(self) -> Dict[str, Any]:
        return {}

    def load_model(self, model_path: str) -> bool:
        return True

    def unload_model(self) -> None:
        pass

    def supports_streaming(self) -> bool:
        return True

    def supports_gpu(self) -> bool:
        return True

    def get_status(self) -> ProviderStatus:
        active = self.registry.get_active_providers()
        if not active:
            return ProviderStatus.UNAVAILABLE
        return ProviderStatus.HEALTHY

    def _get_best_provider(self) -> ILLMProvider:
        active = self.registry.get_active_providers()
        if not active:
            raise RuntimeError("No healthy ILLMProvider available in registry.")
        return active[0]

    def list_models(self) -> List[str]:
        provider = self._get_best_provider()
        return provider.list_models()

    def stream(self, request: LLMRequest) -> Generator[ResponseChunk, None, None]:
        provider = self._get_best_provider()
        self.logger.info(f"LLMRouter routing stream to {provider.name}")
        yield from provider.stream(request)

    def complete(self, request: LLMRequest) -> LLMResponse:
        provider = self._get_best_provider()
        self.logger.info(f"LLMRouter routing complete to {provider.name}")
        return provider.complete(request)
