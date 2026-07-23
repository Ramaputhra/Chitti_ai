from typing import Any, Dict

from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.provider import ProviderStatus
from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.interfaces.llm import ILLMProvider
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

    def health_check(self) -> Dict[str, Any]:
        return {"registry_status": self.registry.health_check()}

    def benchmark(self) -> Dict[str, Any]:
        return {}

    def get_status(self) -> ProviderStatus:
        if not self.registry.get_active_providers():
            return ProviderStatus.UNAVAILABLE
        return ProviderStatus.HEALTHY

    def capabilities(self) -> list[str]:
        return ["text_generation", "tool_calling", "vision"]

    def version(self) -> str:
        return "1.0.0"
        
    def configuration(self) -> Dict[str, Any]:
        return {}

    def get_provider_health(self) -> Any:
        # Stub
        pass

    def _get_best_provider(self, target_model: str = None) -> ILLMProvider:
        # Simplified logic for now: pick the requested provider or the first one
        active = self.registry.get_active_providers()
        if not active:
            raise RuntimeError("No healthy ILLMProvider available.")
            
        if target_model:
            # Attempt to find one that matches
            for p in active:
                if getattr(p, "default_model", None) == target_model or p.name.lower().startswith(target_model.lower()):
                    return p
        return active[0]

    def generate(self, prompt: str, system_prompt: str = "", model: str = None) -> str:
        provider = self._get_best_provider(model)
        self.logger.info(f"LLMRouter routing generate to {provider.name}")
        # Standardize cast based on ILLMProvider (wait, openai has system_prompt, ollama has model)
        # We assume standard ILLMProvider interface: generate(prompt, model=None, system_prompt="") 
        # For now, duck typing
        kwargs = {}
        if system_prompt and "system_prompt" in provider.generate.__code__.co_varnames:
            kwargs["system_prompt"] = system_prompt
        if model and "model" in provider.generate.__code__.co_varnames:
            kwargs["model"] = model
            
        return provider.generate(prompt, **kwargs)

    def stream(self, prompt: str, system_prompt: str = "", model: str = None) -> Any:
        provider = self._get_best_provider(model)
        if hasattr(provider, "stream"):
            return provider.stream(prompt)
        raise NotImplementedError(f"{provider.name} does not support stream()")
