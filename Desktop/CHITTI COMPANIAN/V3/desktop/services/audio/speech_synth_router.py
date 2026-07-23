from typing import Any, Dict, Generator

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import ProviderStatus
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.speech import ISpeechSynthesizer
from desktop.platform.integrations.core.provider_registry import SpeechSynthRegistry


class SpeechSynthRouter(ISpeechSynthesizer):
    def __init__(self, registry: SpeechSynthRegistry, logger: ILoggingService) -> None:
        self.registry = registry
        self.logger = logger
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "SpeechSynthRouter"

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
        return False

    def get_status(self) -> ProviderStatus:
        active = self.registry.get_active_providers()
        if not active:
            return ProviderStatus.UNAVAILABLE
        return ProviderStatus.HEALTHY

    def _get_best_provider(self) -> ISpeechSynthesizer:
        active = self.registry.get_active_providers()
        if not active:
            raise RuntimeError("No healthy ISpeechSynthesizer available in registry.")
        return active[0]

    def synthesize(self, text: str) -> bytes:
        provider = self._get_best_provider()
        self.logger.info(f"SpeechSynthRouter routing synthesize to {provider.name}")
        return provider.synthesize(text)

    def synthesize_stream(self, text: str) -> Generator[bytes, None, None]:
        provider = self._get_best_provider()
        if not provider.supports_streaming():
            self.logger.warning(f"Provider {provider.name} does not support streaming.")
            yield provider.synthesize(text)
            return

        self.logger.info(f"SpeechSynthRouter routing synthesize_stream to {provider.name}")
        yield from provider.synthesize_stream(text)
