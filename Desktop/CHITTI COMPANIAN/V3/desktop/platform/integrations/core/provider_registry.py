from typing import Any, Dict, List

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import IProvider, IProviderRegistry
from desktop.platform.shared.interfaces.service import ServiceState


class ProviderRegistry(IProviderRegistry):
    def __init__(self, registry_name: str, logger: ILoggingService) -> None:
        self.registry_name = registry_name
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._providers: Dict[str, IProvider] = {}
        self._enabled_states: Dict[str, bool] = {}

    @property
    def name(self) -> str:
        return self.registry_name

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        for provider in self._providers.values():
            if provider.state != ServiceState.RUNNING:
                provider.initialize()
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        for provider in self._providers.values():
            if provider.state == ServiceState.RUNNING:
                provider.shutdown()
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {
            name: {
                "enabled": self._enabled_states[name],
                "status": self._providers[name].get_status().name,
                "benchmark": self._providers[name].benchmark()
            }
            for name in self._providers
        }

    def register_provider(self, provider: IProvider, enabled: bool = True) -> None:
        self._providers[provider.name] = provider
        self._enabled_states[provider.name] = enabled
        if self._state == ServiceState.RUNNING and provider.state != ServiceState.RUNNING:
            provider.initialize()
        self.logger.info(f"Registered provider {provider.name} in {self.name} (Enabled: {enabled})")

    def get_provider(self, name: str) -> IProvider:
        if name not in self._providers:
            raise ValueError(f"Provider {name} not found in {self.name}")
        return self._providers[name]

    def get_active_providers(self) -> List[IProvider]:
        return [
            p for name, p in self._providers.items()
            if self._enabled_states[name] and p.get_status().name == "HEALTHY"
        ]

    def enable_provider(self, name: str) -> None:
        if name in self._enabled_states:
            self._enabled_states[name] = True

    def disable_provider(self, name: str) -> None:
        if name in self._enabled_states:
            self._enabled_states[name] = False


class SpeechProviderRegistry(ProviderRegistry):
    def __init__(self, logger: ILoggingService) -> None:
        super().__init__("SpeechProviderRegistry", logger)


class SpeechSynthRegistry(ProviderRegistry):
    def __init__(self, logger: ILoggingService) -> None:
        super().__init__("SpeechSynthRegistry", logger)


class LLMProviderRegistry(ProviderRegistry):
    def __init__(self, logger: ILoggingService) -> None:
        super().__init__("LLMProviderRegistry", logger)
        
        try:
            from desktop.services.ai.providers.llama_cpp_provider import LlamaCppProvider
            self.register(LlamaCppProvider())
        except ImportError:
            logger.error("Failed to register LlamaCppProvider. Missing dependencies?")
        except Exception as e:
            logger.error(f"Failed to register LlamaCppProvider: {e}")
